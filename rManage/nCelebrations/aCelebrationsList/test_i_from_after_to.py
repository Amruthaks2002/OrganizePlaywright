from playwright.sync_api import sync_playwright, expect
from utils.celebrations_helper import open_browser, goto, list_url, expect_celebration_listed, main_content


def test_from_after_to():
    """CEL-009: a From date after the To date shows the empty state without an error."""
    with sync_playwright() as p:
        browser, page = open_browser(p)
        goto(page, list_url(from_date="2026-12-31", to_date="2026-01-01"))

        expect_celebration_listed(page, False)
        expect(main_content(page).get_by_role("heading", name="Celebrations", level=1)).to_be_visible()

        browser.close()
