import re
from playwright.sync_api import sync_playwright, expect
from utils.celebrations_helper import open_browser, open_celebrations, main_content, tab, expect_tab_active


def test_page_loads():
    """CT-001: Celebration Templates opens on the Birthday tab with its header buttons."""
    with sync_playwright() as p:
        browser, page = open_browser(p)
        open_celebrations(page)
        main = main_content(page)
        main.get_by_role("link", name=re.compile("Templates")).click()

        expect(page).to_have_url(re.compile(r"/celebration-templates$"))
        expect(main.get_by_role("heading", name=re.compile("Celebration Templates"), level=1)).to_be_visible()
        expect(main.get_by_text("Manage background templates for birthday and anniversary celebrations")).to_be_visible()
        expect(main.get_by_role("link", name=re.compile("Celebrations"))).to_be_visible()
        expect(main.get_by_role("button", name=re.compile("Add Template"))).to_be_visible()
        expect(tab(page, "Birthday Templates")).to_be_visible()
        expect(tab(page, "Anniversary Templates")).to_be_visible()
        expect_tab_active(page, "Birthday Templates")

        browser.close()
