from playwright.sync_api import sync_playwright, expect
from utils.onboarding_helper import open_browser, open_progress, main_content, DIRECTORY_URL


def test_breadcrumb():
    """JP-012: the Onboarding Dashboard breadcrumb goes to the candidate directory."""
    with sync_playwright() as p:
        browser, page = open_browser(p)
        open_progress(page)

        main_content(page).get_by_role("link", name="Onboarding Dashboard").click()
        expect(page).to_have_url(DIRECTORY_URL)
        expect(main_content(page).get_by_role("heading", name="Employee Onboarding Directory")).to_be_visible()

        browser.close()
