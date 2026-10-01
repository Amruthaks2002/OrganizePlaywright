from playwright.sync_api import sync_playwright, expect
from utils.forms_helper import (
    open_browser, open_my_forms, unique_form_title, create_form_api, delete_forms, search_forms, form_row,
    row_menu_action, delete_dialog,
)


def test_delete_dialog():
    """FM-021: Delete asks for confirmation and warns that responses are deleted too."""
    with sync_playwright() as p:
        browser, page = open_browser(p)
        open_my_forms(page)
        title = unique_form_title()
        try:
            create_form_api(page, title)
            search_forms(page, title)

            row_menu_action(form_row(page, title), "Delete")
            dialog = delete_dialog(page)
            expect(dialog).to_be_visible()
            expect(dialog.get_by_text(
                "Are you sure you want to delete this form? Any responses submitted to this form will also be "
                "permanently deleted. This action cannot be undone.")).to_be_visible()
            expect(dialog.get_by_role("button", name="Cancel")).to_be_visible()
            expect(dialog.get_by_role("button", name="Delete", exact=True)).to_be_visible()
            expect(dialog.get_by_role("button", name="Close")).to_be_visible()
        finally:
            delete_forms(page, title)

        browser.close()
