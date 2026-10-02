import re
from playwright.sync_api import sync_playwright, expect
from utils.celebrations_helper import open_browser, open_celebrations, main_content


def test_templates_button():
    """CEL-011: the Templates button opens Celebration Templates."""
    with sync_playwright() as p:
        browser, page = open_browser(p)
        open_celebrations(page)

        main_content(page).get_by_role("link", name=re.compile("Templates")).click()
        expect(page).to_have_url(re.compile(r"/celebration-templates$"))
        expect(main_content(page).get_by_role("heading", name=re.compile("Celebration Templates"))).to_be_visible()

        browser.close()
