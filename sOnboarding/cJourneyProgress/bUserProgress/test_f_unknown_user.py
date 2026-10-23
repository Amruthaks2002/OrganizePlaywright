from playwright.sync_api import sync_playwright, expect
from utils.onboarding_helper import open_browser, user_progress_url


def test_unknown_user():
    """UP-006: a user id that doesn't exist returns 404."""
    with sync_playwright() as p:
        browser, page = open_browser(p)

        response = page.goto(user_progress_url(999999))
        assert response.status == 404, f"expected 404, got {response.status}"
        expect(page.get_by_text("Not Found").first).to_be_visible()

        browser.close()
