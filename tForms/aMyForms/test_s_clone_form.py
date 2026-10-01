import re
from playwright.sync_api import sync_playwright, expect
from utils.forms_helper import (
    open_browser, open_my_forms, unique_form_title, create_form_api, question, delete_forms, search_forms,
    form_row, row_menu_action, main_content, goto, settle,
)


def test_clone_form():
    """FM-019: Clone adds "<title> (Copy)" with the same questions."""
    with sync_playwright() as p:
        browser, page = open_browser(p)
        open_my_forms(page)
        title = unique_form_title()
        try:
            create_form_api(page, title, [question("Your name"), question("Colour", "multiple_choice", ["Red", "Blue"])])
            search_forms(page, title)

            row_menu_action(form_row(page, title), "Clone")
            settle(page)
            search_forms(page, title)
            copy = form_row(page, f"{title} (Copy)")
            expect(copy).to_have_count(1)
            expect(form_row(page, title)).to_have_count(1)

            goto(page, copy.get_by_title("Preview Form").get_attribute("href"))
            main = main_content(page)
            expect(main.get_by_role("heading", name=f"{title} (Copy)")).to_be_visible()
            expect(main.locator("h3")).to_have_text([re.compile(r"1\. Your name"), re.compile(r"2\. Colour")])
            expect(main.locator("label").filter(has=page.locator("input[type=radio]"))).to_have_text(["Red", "Blue"])
        finally:
            delete_forms(page, title)

        browser.close()
