import re
from playwright.sync_api import sync_playwright, expect
from utils.forms_helper import (
    open_browser, open_my_forms, unique_form_title, create_form_api, delete_forms, search_forms, form_row,
    row_menu_action, main_content,
)


def test_edit_action():
    """FM-020: Edit opens the form in the editor."""
    with sync_playwright() as p:
        browser, page = open_browser(p)
        open_my_forms(page)
        title = unique_form_title()
        try:
            form = create_form_api(page, title)
            search_forms(page, title)

            row_menu_action(form_row(page, title), "Edit")
            expect(page).to_have_url(re.compile(rf"/forms/{form['id']}/edit$"))
            expect(main_content(page).get_by_role("heading", name=f"Edit Form: {title}")).to_be_visible()
        finally:
            delete_forms(page, title)

        browser.close()
