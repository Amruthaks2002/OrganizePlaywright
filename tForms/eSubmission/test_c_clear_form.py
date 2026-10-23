from playwright.sync_api import sync_playwright, expect
from utils.forms_helper import (
    open_browser, unique_form_title, create_form_api, question, delete_forms, goto, submission_url,
    public_form, public_question, answer_input,
)


def test_clear_form():
    """SB-003: Clear Form empties every answer."""
    with sync_playwright() as p:
        browser, page = open_browser(p)
        title = unique_form_title()
        try:
            form = create_form_api(page, title, [
                question("Name"), question("Colour", "multiple_choice", ["Red", "Blue"]),
                question("Pets", "checkbox", ["Cat", "Dog"]),
            ])
            goto(page, submission_url(form))
            answer_input(page, "Name").fill("Sam")
            public_question(page, "Colour").get_by_label("Blue").check()
            public_question(page, "Pets").get_by_label("Dog").check()

            public_form(page).get_by_role("button", name="Clear Form").click()
            expect(answer_input(page, "Name")).to_have_value("")
            expect(public_question(page, "Colour").get_by_label("Blue")).not_to_be_checked()
            expect(public_question(page, "Pets").get_by_label("Dog")).not_to_be_checked()
        finally:
            delete_forms(page, title)

        browser.close()
