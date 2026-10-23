from playwright.sync_api import sync_playwright, expect
from utils.forms_helper import (
    open_browser, unique_form_title, create_form_api, delete_forms, goto, responses_url, main_content,
    submission_url,
)


def test_no_responses():
    """RS-001: a form without responses shows "No responses yet" and a link to the public form."""
    with sync_playwright() as p:
        browser, page = open_browser(p)
        title = unique_form_title()
        try:
            form = create_form_api(page, title)
            goto(page, responses_url(form))
            main = main_content(page)

            expect(main.get_by_role("heading", name=title)).to_be_visible()
            expect(main.get_by_text("No responses yet")).to_be_visible()
            expect(main.get_by_text("Share your form to start collecting responses from your audience.")).to_be_visible()
            expect(main.get_by_role("link", name="Open Public Form")).to_have_attribute("href", submission_url(form))
        finally:
            delete_forms(page, title)

        browser.close()
