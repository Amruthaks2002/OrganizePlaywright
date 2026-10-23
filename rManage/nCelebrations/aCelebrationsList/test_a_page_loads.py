import re
from playwright.sync_api import sync_playwright, expect
from utils.celebrations_helper import open_browser, open_celebrations, main_content


def test_page_loads():
    """CEL-001: Manage > Celebrations opens the celebrations page with its header buttons."""
    with sync_playwright() as p:
        browser, page = open_browser(p)
        open_celebrations(page)
        main = main_content(page)

        expect(page).to_have_url(re.compile(r"/celebrations$"))
        expect(main.get_by_role("heading", name="Celebrations", level=1)).to_be_visible()
        expect(main.get_by_text("Manage upcoming birthdays and work anniversaries")).to_be_visible()
        expect(main.get_by_role("link", name=re.compile("Templates"))).to_be_visible()
        expect(main.get_by_role("link", name=re.compile("Announcements"))).to_be_visible()

        browser.close()
