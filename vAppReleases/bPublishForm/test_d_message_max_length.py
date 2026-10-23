from playwright.sync_api import sync_playwright, expect
from utils.app_releases_helper import open_browser, open_releases, field


def test_message_max_length():
    """AR-008: both update messages stop at 500 characters."""
    with sync_playwright() as p:
        browser, page = open_browser(p)
        open_releases(page)

        for name in ["optional_message", "mandatory_message"]:
            expect(field(page, name)).to_have_attribute("maxlength", "500")
            field(page, name).fill("x" * 600)
            assert len(field(page, name).input_value()) == 500, name

        browser.close()
