from playwright.sync_api import sync_playwright, expect
from utils.forms_helper import open_browser, open_create_form, question_cards, question_input, add_field_buttons


def test_add_question_at_top():
    """CF-011: the + under the description inserts a new question above the others."""
    with sync_playwright() as p:
        browser, page = open_browser(p)
        open_create_form(page)
        question_input(question_cards(page).first).fill("Existing question")

        add_field_buttons(page).first.click()
        expect(question_cards(page)).to_have_count(2)
        expect(question_input(question_cards(page).nth(0))).to_have_value("")
        expect(question_input(question_cards(page).nth(1))).to_have_value("Existing question")

        browser.close()
