from playwright.sync_api import sync_playwright, expect
from utils.forms_helper import (
    open_browser, unique_form_title, create_form_api, question, delete_forms, goto, submission_url,
    answer_input, submit_button, thank_you,
)


def test_cannot_edit_response():
    """SB-005: when response editing is off, reopening the link after submitting says "Cannot Edit Response"."""
    with sync_playwright() as p:
        browser, page = open_browser(p)
        title = unique_form_title()
        try:
            form = create_form_api(page, title, [question("Name")])
            goto(page, submission_url(form))
            answer_input(page, "Name").fill("Sam")
            submit_button(page).click()
            expect(thank_you(page)).to_be_visible()

            goto(page, submission_url(form))
            expect(submit_button(page)).to_have_text("Cannot Edit Response")
            expect(submit_button(page)).to_be_disabled()
        finally:
            delete_forms(page, title)

        browser.close()
