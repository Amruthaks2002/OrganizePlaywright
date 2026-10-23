import pytest
from playwright.sync_api import expect


@pytest.fixture(autouse=True)
def patient_expect():
    """Gives expect() 15s instead of 5s in the marketplace tests: approve / reject / upload
    redirect and re-render the whole page, which can take longer than 5s on QC. Restored after
    each test so other suites in the same worker keep the default."""
    expect.set_options(timeout=15_000)
    yield
    expect.set_options(timeout=5_000)
