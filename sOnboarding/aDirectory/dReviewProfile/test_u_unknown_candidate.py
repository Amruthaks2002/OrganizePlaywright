from playwright.sync_api import sync_playwright, expect
from utils.onboarding_helper import open_browser, review_url


def test_unknown_candidate():
    """RP-022: a candidate id that doesn't exist returns 404."""
    with sync_playwright() as p:
        browser, page = open_browser(p)

        response = page.goto(review_url(999999))
        assert response.status == 404, f"expected 404, got {response.status}"
        expect(page.get_by_text("Not Found").first).to_be_visible()

        browser.close()
