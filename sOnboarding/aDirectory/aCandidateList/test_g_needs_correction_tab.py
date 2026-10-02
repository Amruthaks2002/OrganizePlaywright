import re
from playwright.sync_api import sync_playwright, expect
from utils.onboarding_helper import (
    open_browser, open_directory, status_tab, candidate_rows, row_statuses, settle, STATUS_BADGES,
)


def test_needs_correction_tab():
    """OD-007: the Needs Correction tab puts status=needs_correction in the URL and lists only candidates with that status."""
    with sync_playwright() as p:
        browser, page = open_browser(p)
        open_directory(page)

        status_tab(page, "Needs Correction").click()
        expect(page).to_have_url(re.compile(r"status=needs_correction"))
        settle(page)
        expect(candidate_rows(page).first).to_be_visible()
        assert row_statuses(page) == {STATUS_BADGES["needs_correction"]}, row_statuses(page)

        browser.close()
