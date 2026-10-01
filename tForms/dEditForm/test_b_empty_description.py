from playwright.sync_api import sync_playwright, expect
from utils.forms_helper import (
    open_browser, unique_form_title, create_form_api, delete_forms, goto, edit_url, main_content,
)


def test_empty_description():
    """EF-001b: a form without a description shows "No description added" in the editor."""
    with sync_playwright() as p:
        browser, page = open_browser(p)
        title = unique_form_title()
        try:
            form = create_form_api(page, title)
            goto(page, edit_url(form))
            expect(main_content(page).get_by_text("No description added")).to_be_visible()
        finally:
            delete_forms(page, title)

        browser.close()
