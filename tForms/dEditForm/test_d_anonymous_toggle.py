from playwright.sync_api import sync_playwright, expect
from utils.forms_helper import (
    open_browser, unique_form_title, create_form_api, delete_forms, goto, edit_url, anonymous_button,
    expect_toast, header_button, share_dialog, dialog_setting,
)


def test_anonymous_toggle():
    """EF-003: Anonymous turns on anonymous responses for a saved form."""
    with sync_playwright() as p:
        browser, page = open_browser(p)
        title = unique_form_title()
        try:
            form = create_form_api(page, title)
            goto(page, edit_url(form))

            anonymous_button(page).click()
            expect_toast(page, "Anonymous responses enabled.")

            goto(page, edit_url(form))
            header_button(page, "Share").click()
            expect(dialog_setting(share_dialog(page), "Anonymous responses")).to_have_text("Enabled")
        finally:
            delete_forms(page, title)

        browser.close()
