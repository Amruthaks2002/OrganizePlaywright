import re
from playwright.sync_api import sync_playwright, expect
from utils.forms_helper import open_browser, open_my_forms, main_content, title_input


def test_new_form_button():
    """FM-013: New Form opens the Create Form page."""
    with sync_playwright() as p:
        browser, page = open_browser(p)
        open_my_forms(page)

        main_content(page).get_by_role("link", name=re.compile("New Form")).click()
        expect(page).to_have_url(re.compile(r"/forms/create$"))
        expect(main_content(page).get_by_role("heading", name="Create New Form")).to_be_visible()
        expect(title_input(page)).to_be_visible()

        browser.close()
