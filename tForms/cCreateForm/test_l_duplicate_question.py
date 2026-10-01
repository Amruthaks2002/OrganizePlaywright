import re
from playwright.sync_api import sync_playwright, expect
from utils.forms_helper import (
    open_browser, open_create_form, question_cards, question_input, fill_question, type_button, option_inputs,
    required_toggle, expect_toggle_on,
)


def test_duplicate_question():
    """CF-012: Duplicate copies a question's text, type, options and required setting."""
    with sync_playwright() as p:
        browser, page = open_browser(p)
        open_create_form(page)
        fill_question(question_cards(page).first, "Favourite colour", "Check Box", ("Red", "Blue"), required=True)

        question_cards(page).first.get_by_title("Duplicate").click()
        expect(question_cards(page)).to_have_count(2)
        copy = question_cards(page).nth(1)
        expect(question_input(copy)).to_have_value("Favourite colour")
        expect(type_button(copy)).to_have_text(re.compile(r"Check Box"))
        expect(option_inputs(copy)).to_have_count(2)
        assert [option_inputs(copy).nth(i).input_value() for i in range(2)] == ["Red", "Blue"]
        expect_toggle_on(required_toggle(copy))

        browser.close()
