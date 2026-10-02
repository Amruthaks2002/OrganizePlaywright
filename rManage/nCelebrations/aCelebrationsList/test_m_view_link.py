import re
from playwright.sync_api import sync_playwright, expect
from utils.celebrations_helper import (
    open_browser, goto, wide_list_url, celebration_card, main_content, CELEBRATION_ID,
)


def test_view_link():
    """CEL-013: View on a celebration card opens its Prepare Celebration page."""
    with sync_playwright() as p:
        browser, page = open_browser(p)
        goto(page, wide_list_url())

        celebration_card(page).get_by_role("link", name="View").click()
        expect(page).to_have_url(re.compile(rf"/celebrations/{CELEBRATION_ID}/edit$"))
        expect(main_content(page).get_by_role("heading", name="Prepare Celebration")).to_be_visible()

        browser.close()
