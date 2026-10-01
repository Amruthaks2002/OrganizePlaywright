import re
from playwright.sync_api import sync_playwright, expect
from utils.forms_helper import (
    open_browser, unique_form_title, create_form_api, toggle_status_api, delete_forms, goto, submission_url,
    closed_page,
)


def test_closed_back_to_home():
    """SB-008: the "Form Closed" page has a Back to Home link to the dashboard."""
    with sync_playwright() as p:
        browser, page = open_browser(p)
        title = unique_form_title()
        try:
            form = create_form_api(page, title)
            toggle_status_api(page, form["id"])
            goto(page, submission_url(form))
            expect(page.get_by_role("heading", name="Form Closed")).to_be_visible()
            expect(closed_page(page, title)).to_be_visible()
            expect(page.get_by_text("This form has reached its response limit or the submission deadline has passed.")) \
                .to_be_visible()

            page.get_by_role("link", name="Back to Home").click()
            expect(page).to_have_url(re.compile(r"/dashboard$"))
        finally:
            delete_forms(page, title)

        browser.close()
