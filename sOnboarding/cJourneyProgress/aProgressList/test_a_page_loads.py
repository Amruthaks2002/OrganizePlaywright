from playwright.sync_api import sync_playwright, expect
from utils.onboarding_helper import (
    open_browser, open_onboarding_submenu, main_content, progress_search, progress_rows, PROGRESS_URL,
)


def test_page_loads():
    """JP-001: Onboarding > Journey Progress lists employees' journey progress with search, filters and Clear."""
    with sync_playwright() as p:
        browser, page = open_browser(p)
        open_onboarding_submenu(page, "journey-progress")
        main = main_content(page)

        expect(page).to_have_url(PROGRESS_URL)
        expect(main.get_by_role("link", name="Onboarding Dashboard")).to_be_visible()
        expect(main.get_by_role("heading", name="Employee Journey Progress")).to_be_visible()
        expect(main.get_by_text("Monitor the step-by-step progress, completion rates, and quiz statuses")).to_be_visible()
        expect(progress_search(page)).to_be_visible()
        for placeholder in ["All Roles", "All Journeys", "All Statuses"]:
            expect(main.get_by_placeholder(placeholder)).to_be_visible()
        expect(main.get_by_role("button", name="Clear", exact=True)).to_be_visible()
        for column in ["EMPLOYEE", "JOURNEY", "PROGRESS", "STATUS", "ACTIONS"]:
            expect(main.locator("thead")).to_contain_text(column, ignore_case=True)
        expect(progress_rows(page)).to_have_count(10)

        browser.close()
