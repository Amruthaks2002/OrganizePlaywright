from playwright.sync_api import sync_playwright, expect
from utils.forms_helper import (
    open_browser, open_create_form, unique_form_title, delete_forms, title_input, question_cards,
    question_input, add_question, save_button, expect_toast,
)


def test_question_text_required():
    """CF-003: a question without text can't be saved."""
    with sync_playwright() as p:
        browser, page = open_browser(p)
        open_create_form(page)
        title = unique_form_title()
        try:
            title_input(page).fill(title)
            add_question(page)
            question_input(question_cards(page).nth(1)).fill("")

            save_button(page).click()
            expect_toast(page, "The questions.1.question field is required.")
            expect(question_cards(page).nth(1).get_by_text("The questions.1.question field is required.")) \
                .to_be_visible()
            expect(page.get_by_role("heading", name="Form Created Successfully")).to_have_count(0)
        finally:
            delete_forms(page, title)

        browser.close()
