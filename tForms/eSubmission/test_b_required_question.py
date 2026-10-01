from playwright.sync_api import sync_playwright, expect
from utils.forms_helper import (
    open_browser, unique_form_title, create_form_api, question, delete_forms, goto, submission_url,
    public_question, submit_button, thank_you, expect_toast, answer_input,
)


def test_required_question():
    """SB-002: submitting without answering a required question shows "Required." under it."""
    with sync_playwright() as p:
        browser, page = open_browser(p)
        title = unique_form_title()
        try:
            form = create_form_api(page, title, [question("Mandatory", required=True), question("Optional")])
            goto(page, submission_url(form))

            answer_input(page, "Optional").fill("Only the optional one")
            submit_button(page).click()
            expect_toast(page, "Required.")
            expect(public_question(page, "Mandatory").get_by_text("Required.")).to_be_visible()
            expect(public_question(page, "Optional").get_by_text("Required.")).to_have_count(0)
            expect(thank_you(page)).to_have_count(0)
        finally:
            delete_forms(page, title)

        browser.close()
