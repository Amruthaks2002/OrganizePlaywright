import os

import pytest
from playwright.sync_api import expect, sync_playwright
from utils.work_summary_bulk_helper import CREATED_LOG_IDS, mark_notifications_read, sign_in_page

# who gets notified about comp entries the tests log or reject (and can be signed in to)
NOTIFIED_ROLES = ["admin", "hr", "team-lead", "project-manager", "employee"]


@pytest.fixture(autouse=True)
def patient_expect():
    """Gives expect() 15s instead of 5s: bulk actions redirect and refetch the whole table, which can take
    longer than 5s on QC. Restored after each test so other suites in the same worker keep the default."""
    expect.set_options(timeout=15_000)
    yield
    expect.set_options(timeout=5_000)


@pytest.fixture(scope="session", autouse=True)
def read_test_notifications():
    """Logging comp hours notifies the approvers, and rejecting notifies the employee (and HR / the team lead).
    Notifications can't be deleted, so once the bulk tests are done, mark the ones about their logs as read to
    leave everyone's unread count as it was."""
    yield
    if not CREATED_LOG_IDS:
        return
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=os.environ.get("HEADLESS") == "1")
        try:
            for role in NOTIFIED_ROLES:
                # QC sometimes drops a connection; one retry is enough
                for attempt in (1, 2):
                    try:
                        mark_notifications_read(sign_in_page(browser, role), CREATED_LOG_IDS)
                        break
                    except Exception:
                        if attempt == 2:
                            raise
        finally:
            browser.close()
