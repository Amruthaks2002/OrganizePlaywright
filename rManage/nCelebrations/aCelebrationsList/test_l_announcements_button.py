import re
from playwright.sync_api import sync_playwright, expect
from utils.celebrations_helper import open_browser, open_celebrations, main_content


def test_announcements_button():
    """CEL-012: the Announcements button opens the Announcements Manager."""
    with sync_playwright() as p:
        browser, page = open_browser(p)
        open_celebrations(page)

        main_content(page).get_by_role("link", name=re.compile("Announcements")).click()
        expect(page).to_have_url(re.compile(r"/announcements/manage$"))
        expect(main_content(page).get_by_role("heading", name=re.compile("Announcements Manager"))).to_be_visible()

        browser.close()
