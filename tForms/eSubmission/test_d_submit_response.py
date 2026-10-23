from playwright.sync_api import sync_playwright, expect
from utils.forms_helper import (
    open_browser, unique_form_title, create_form_api, question, delete_forms, goto, submission_url,
    public_question, answer_input, submit_button, thank_you, expect_toast, public_form,
)


def test_submit_response():
    """SB-004: a valid submission shows the thank-you message and offers "Submit another response"."""
    with sync_playwright() as p:
        browser, page = open_browser(p)
        title = unique_form_title()
        try:
            form = create_form_api(page, title, [question("Name", required=True),
                                                 question("Colour", "multiple_choice", ["Red", "Blue"])])
            goto(page, submission_url(form))
            answer_input(page, "Name").fill("Sam")
            public_question(page, "Colour").get_by_label("Red").check()

            submit_button(page).click()
            expect_toast(page, "Submitted successfully")
            expect(page.get_by_role("heading", name=title)).to_be_visible()
            expect(thank_you(page)).to_be_visible()

            page.get_by_role("button", name="Submit another response").click()
            expect(public_form(page)).to_be_visible()
            expect(answer_input(page, "Name")).to_have_value("")
        finally:
            delete_forms(page, title)

        browser.close()
