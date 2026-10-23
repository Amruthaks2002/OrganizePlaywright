import re
from playwright.sync_api import sync_playwright, expect
from utils.onboarding_helper import (
    open_browser, open_directory, status_tab, candidate_rows, row_statuses, settle, STATUS_BADGES,
)


def test_in_progress_tab():
    """OD-005: the In Progress tab puts status=in_progress in the URL and lists only candidates with that status."""
    with sync_playwright() as p:
        browser, page = open_browser(p)
        open_directory(page)

        status_tab(page, "In Progress").click()
        expect(page).to_have_url(re.compile(r"status=in_progress"))
        settle(page)
        expect(candidate_rows(page).first).to_be_visible()
        assert row_statuses(page) == {STATUS_BADGES["in_progress"]}, row_statuses(page)

        browser.close()
