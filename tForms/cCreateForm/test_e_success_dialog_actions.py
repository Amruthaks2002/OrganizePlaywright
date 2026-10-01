import re
from playwright.sync_api import sync_playwright, expect
from utils.forms_helper import (
    open_browser, open_create_form, unique_form_title, delete_forms, build_form, save_new_form, success_dialog,
    submission_url, main_content,
)


def test_success_dialog_actions():
    """CF-005: the success dialog's Copy Link copies the public link and Go to Dashboard opens My Forms."""
    with sync_playwright() as p:
        browser, page = open_browser(p)
        page.context.grant_permissions(["clipboard-read", "clipboard-write"])
        open_create_form(page)
        title = unique_form_title()
        try:
            build_form(page, title)
            form = save_new_form(page)
            dialog = success_dialog(page)

            dialog.get_by_role("button", name="Copy Link").click()
            page.wait_for_timeout(500)
            assert page.evaluate("navigator.clipboard.readText()") == submission_url(form)

            dialog.get_by_role("link", name="Go to Dashboard").click()
            expect(page).to_have_url(re.compile(r"/forms$"))
            expect(main_content(page).get_by_role("heading", name="My Forms")).to_be_visible()
        finally:
            delete_forms(page, title)

        browser.close()
