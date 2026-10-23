from playwright.sync_api import sync_playwright, expect
from utils.onboarding_helper import open_browser, open_user_progress, main_content, PROGRESS_URL, DIRECTORY_URL, COMPLETED_USER_ID


def test_breadcrumb():
    """UP-005: the Journey Progress and Onboarding Dashboard breadcrumbs navigate back."""
    with sync_playwright() as p:
        browser, page = open_browser(p)
        open_user_progress(page, COMPLETED_USER_ID)
        main = main_content(page)
        expect(main.get_by_text("User Progress")).to_be_visible()

        main.get_by_role("link", name="Journey Progress").click()
        expect(page).to_have_url(PROGRESS_URL)

        open_user_progress(page, COMPLETED_USER_ID)
        main.get_by_role("link", name="Onboarding Dashboard").click()
        expect(page).to_have_url(DIRECTORY_URL)

        browser.close()
