import re
from playwright.sync_api import sync_playwright, expect
from utils.onboarding_helper import open_browser, open_progress, progress_url, main_content, vue_select, progress_rows, progress_values, settle


def test_status_filter():
    """JP-008: the status filter shows only Completed (100%) or only In Progress employees."""
    with sync_playwright() as p:
        browser, page = open_browser(p)
        open_progress(page)

        vue_select(page, main_content(page), "All Statuses", "Completed")
        expect(page).to_have_url(re.compile(r"status=completed"))
        settle(page)
        expect(progress_rows(page).first).to_be_visible()
        assert {status for *_, status in progress_values(page)} == {"COMPLETED"}, progress_values(page)

        open_progress(page, progress_url(status="in_progress"))
        expect(progress_rows(page).first).to_be_visible()
        assert {status for *_, status in progress_values(page)} == {"IN PROGRESS"}, progress_values(page)

        browser.close()
