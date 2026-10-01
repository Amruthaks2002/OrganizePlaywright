from playwright.sync_api import sync_playwright, expect
from utils.forms_helper import (
    open_browser, unique_form_title, create_form_api, question, delete_forms, goto, edit_url, open_settings,
    settings_toggle, expect_toast, submission_url, answer_input, submit_button, thank_you, closed_page,
)


def test_response_limit_closes_form():
    """EF-006: with "After number of responses" set to 1 the form closes after the first response."""
    with sync_playwright() as p:
        browser, page = open_browser(p)
        title = unique_form_title()
        try:
            form = create_form_api(page, title, [question("Your name")])
            goto(page, edit_url(form))
            panel = open_settings(page)
            settings_toggle(panel, "After number of responses").click()
            panel.get_by_placeholder("Max responses").fill("1")
            panel.get_by_role("button", name="Save").click()
            expect_toast(page, "Form saved successfully.")

            goto(page, submission_url(form))
            answer_input(page, "Your name").fill("First responder")
            submit_button(page).click()
            expect(thank_you(page)).to_be_visible()

            # someone else opening the link now finds it closed
            visitor = browser.new_context().new_page()
            visitor.goto(submission_url(form))
            expect(visitor.get_by_role("heading", name="Form Closed")).to_be_visible()
            expect(closed_page(visitor, title)).to_be_visible()
            visitor.context.close()
        finally:
            delete_forms(page, title)

        browser.close()
