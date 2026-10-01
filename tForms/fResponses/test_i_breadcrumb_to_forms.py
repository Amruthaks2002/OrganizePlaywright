import re
from playwright.sync_api import sync_playwright, expect
from utils.forms_helper import (
    open_browser, unique_form_title, create_form_api, delete_forms, goto, responses_url, main_content,
)


def test_breadcrumb_to_forms():
    """RS-009: the Forms breadcrumb on the responses page goes back to My Forms."""
    with sync_playwright() as p:
        browser, page = open_browser(p)
        title = unique_form_title()
        try:
            form = create_form_api(page, title)
            goto(page, responses_url(form))

            main_content(page).get_by_role("link", name="Forms", exact=True).click()
            expect(page).to_have_url(re.compile(r"/forms$"))
            expect(main_content(page).get_by_role("heading", name="My Forms")).to_be_visible()
        finally:
            delete_forms(page, title)

        browser.close()
