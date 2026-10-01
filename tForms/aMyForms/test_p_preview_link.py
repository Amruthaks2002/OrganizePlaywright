import re
from playwright.sync_api import sync_playwright, expect
from utils.forms_helper import (
    open_browser, open_my_forms, unique_form_title, create_form_api, question, delete_forms, search_forms,
    form_row, main_content,
)


def test_preview_link():
    """FM-016: the eye icon opens a preview of the form."""
    with sync_playwright() as p:
        browser, page = open_browser(p)
        open_my_forms(page)
        title = unique_form_title()
        try:
            form = create_form_api(page, title, [question("Your name"), question("Your team")])
            search_forms(page, title)

            form_row(page, title).get_by_title("Preview Form").click()
            expect(page).to_have_url(re.compile(rf"/forms/{form['id']}$"))
            main = main_content(page)
            expect(main.get_by_role("button", name="Back to Editor")).to_be_visible()
            expect(main.get_by_role("heading", name=title)).to_be_visible()
            expect(main.locator("h3")).to_have_text([re.compile(r"1\. Your name"), re.compile(r"2\. Your team")])
        finally:
            delete_forms(page, title)

        browser.close()
