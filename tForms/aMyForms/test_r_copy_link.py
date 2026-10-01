from playwright.sync_api import sync_playwright
from utils.forms_helper import (
    open_browser, open_my_forms, unique_form_title, create_form_api, delete_forms, search_forms, form_row,
    row_menu_action, expect_toast, submission_url,
)


def test_copy_link():
    """FM-018: Copy Link copies the form's public submission link."""
    with sync_playwright() as p:
        browser, page = open_browser(p)
        page.context.grant_permissions(["clipboard-read", "clipboard-write"])
        open_my_forms(page)
        title = unique_form_title()
        try:
            form = create_form_api(page, title)
            search_forms(page, title)

            row_menu_action(form_row(page, title), "Copy Link")
            expect_toast(page, "Form link copied to clipboard!")
            assert page.evaluate("navigator.clipboard.readText()") == submission_url(form)
        finally:
            delete_forms(page, title)

        browser.close()
