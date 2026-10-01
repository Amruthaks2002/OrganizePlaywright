from playwright.sync_api import sync_playwright, expect
from utils.forms_helper import (
    open_browser, open_create_form, question_cards, question_input, add_field_buttons, type_button,
)


def test_add_question_at_end():
    """CF-010: the + under the last question adds a new empty question at the end."""
    with sync_playwright() as p:
        browser, page = open_browser(p)
        open_create_form(page)
        question_input(question_cards(page).first).fill("First question")

        add_field_buttons(page).last.click()
        expect(question_cards(page)).to_have_count(2)
        expect(question_input(question_cards(page).nth(0))).to_have_value("First question")
        expect(question_input(question_cards(page).nth(1))).to_have_value("")
        expect(type_button(question_cards(page).nth(1))).to_have_text("Short Answer")

        browser.close()
