import re
from playwright.sync_api import sync_playwright, expect
from utils.celebrations_helper import open_browser, open_templates, main_content


def test_celebrations_button():
    """CT-003: the Celebrations button returns to the celebrations list."""
    with sync_playwright() as p:
        browser, page = open_browser(p)
        open_templates(page)

        main_content(page).get_by_role("link", name=re.compile("Celebrations")).click()
        expect(page).to_have_url(re.compile(r"/celebrations$"))
        expect(main_content(page).get_by_role("heading", name="Celebrations", level=1)).to_be_visible()

        browser.close()
