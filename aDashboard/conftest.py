# Lets the dashboard tests run in parallel (pytest aDashboard -n 4).
#
# Tests that change or count the same QC data must not run at the same time, and some depend
# on running in order (the legacy note tests add, then edit, then delete one note). Each such
# folder becomes an xdist group: a group runs in order on a single worker, and different groups -
# plus the read-only tests, which get no group - run side by side.
import sys
from pathlib import Path

import pytest
from playwright.sync_api import expect

HERE = Path(__file__).parent

# read-only folders: their tests can run on any worker at any time
READ_ONLY = {"aProfileCard", "bAttendance", "gHeader"}


def pytest_configure(config):
    # with -n, xdist defaults to --dist load, which ignores groups; use loadgroup instead
    # unless --dist was given on the command line
    worker_input = getattr(config, "workerinput", None)
    argv = worker_input["mainargv"] if worker_input else sys.argv
    if any(arg == "-d" or arg.startswith("--dist") for arg in argv):
        return
    if worker_input:
        # workers re-read the original command line (--dist load) and decide whether to tag tests
        # with their group before this hook runs, so tell them here too
        config.option.loadgroup = True
    elif getattr(config.option, "dist", "no") == "load":
        config.option.dist = "loadgroup"


@pytest.hookimpl(tryfirst=True)  # xdist reads the group markers in its own hook, so add them before that runs
def pytest_collection_modifyitems(config, items):
    for item in items:
        path = Path(item.fspath)
        if HERE not in path.parents:
            continue
        folder = path.relative_to(HERE).parts[0]
        if folder not in READ_ONLY:
            # cTasks: task counts move when another task test adds or starts a task
            # dUpcomingEvents: the event test changes the count the other tests read
            # eCalendar / fCalendarNotes: notes and chip counts on the same calendar
            item.add_marker(pytest.mark.xdist_group(f"aDashboard-{folder}"))


@pytest.fixture(autouse=True)
def patient_expect():
    """Gives expect() 15s instead of 5s in the dashboard tests: with several workers on the same QC
    server, a dropdown or a page change can take longer than 5s. Restored after each test so other
    suites in the same worker keep the default."""
    expect.set_options(timeout=15_000)
    yield
    expect.set_options(timeout=5_000)
