from playwright.sync_api import sync_playwright, expect
from utils.forms_helper import (
    open_browser, open_my_forms, unique_form_title, create_form_api, delete_forms, search_forms, form_row,
    row_menu_action, delete_dialog,
)


def test_close_delete_dialog():
    """FM-023: the X closes the delete dialog and keeps the form."""
    with sync_playwright() as p:
        browser, page = open_browser(p)
        open_my_forms(page)
        title = unique_form_title()
        try:
            create_form_api(page, title)
            search_forms(page, title)

            row_menu_action(form_row(page, title), "Delete")
            delete_dialog(page).get_by_role("button", name="Close").click()
            expect(delete_dialog(page)).to_be_hidden()

            search_forms(page, title)
            expect(form_row(page, title)).to_have_count(1)
        finally:
            delete_forms(page, title)

        browser.close()
