from playwright.sync_api import sync_playwright, expect
from utils.celebrations_helper import open_browser, prepare_url


def test_unknown_celebration():
    """PC-008: a celebration id that doesn't exist returns 404."""
    with sync_playwright() as p:
        browser, page = open_browser(p)

        response = page.goto(prepare_url(999999))
        assert response.status == 404, f"expected 404, got {response.status}"
        expect(page.get_by_text("Not Found", exact=False).first).to_be_visible()

        browser.close()
