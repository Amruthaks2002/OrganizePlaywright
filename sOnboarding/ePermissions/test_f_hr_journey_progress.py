from playwright.sync_api import sync_playwright, expect
from utils.onboarding_helper import (
    open_browser_as, open_onboarding_submenu, progress_rows, progress_row, user_progress_url, main_content,
    progress_url, open_progress, PROGRESS_URL, COMPLETED_USER, COMPLETED_USER_ID,
)


def test_hr_journey_progress():
    """PM-006: HR sees the Onboarding menu and can follow employees' journey progress."""
    with sync_playwright() as p:
        browser, page = open_browser_as(p, "hr")

        open_onboarding_submenu(page, "journey-progress")
        expect(page).to_have_url(PROGRESS_URL)
        expect(progress_rows(page).first).to_be_visible()

        open_progress(page, progress_url(search=COMPLETED_USER))
        progress_row(page, COMPLETED_USER).get_by_role("link", name="View Journey Progress").click()
        expect(page).to_have_url(user_progress_url(COMPLETED_USER_ID))
        expect(main_content(page).get_by_role("heading", name="Onboarding Progress")).to_be_visible()

        browser.close()
