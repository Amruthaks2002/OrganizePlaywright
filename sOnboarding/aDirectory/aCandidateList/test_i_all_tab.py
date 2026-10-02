import re
from playwright.sync_api import sync_playwright, expect
from utils.onboarding_helper import open_browser, open_directory, status_tab, row_statuses, settle


def test_all_tab():
    """OD-009: the All tab clears the status filter and lists candidates of every status
    (there's an In Progress and an Approved "lijo")."""
    with sync_playwright() as p:
        browser, page = open_browser(p)
        open_directory(page, search="lijo", status="approved")
        assert row_statuses(page) == {"Approved"}

        status_tab(page, "All").click()
        expect(page).to_have_url(re.compile(r"status=(&|$)"))
        settle(page)
        assert {"In Progress", "Approved"} <= row_statuses(page), row_statuses(page)

        browser.close()
