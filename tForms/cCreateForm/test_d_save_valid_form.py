from playwright.sync_api import sync_playwright, expect
from utils.forms_helper import (
    open_browser, open_create_form, unique_form_title, delete_forms, build_form, save_new_form, success_dialog,
    dialog_setting, goto, FORMS_URL, search_forms, form_row,
)


def test_save_valid_form():
    """CF-004: saving a valid form shows the success dialog with the default settings."""
    with sync_playwright() as p:
        browser, page = open_browser(p)
        open_create_form(page)
        title = unique_form_title()
        try:
            build_form(page, title, [("Your name", "Short Answer", (), False),
                                     ("Colour", "Multiple Choice", ("Red", "Blue"), False)])
            form = save_new_form(page)
            assert form["title"] == title

            dialog = success_dialog(page)
            expect(dialog).to_be_visible()
            expect(dialog.get_by_text("Your form has been created and is ready to accept responses.")).to_be_visible()
            expect(dialog_setting(dialog, "Stop accepting responses on")).to_have_text("No date set")
            expect(dialog_setting(dialog, "Stop accepting responses after")).to_have_text("No limit set")
            expect(dialog_setting(dialog, "Anonymous responses")).to_have_text("Disabled")

            goto(page, FORMS_URL)
            search_forms(page, title)
            expect(form_row(page, title)).to_have_count(1)
        finally:
            delete_forms(page, title)

        browser.close()
