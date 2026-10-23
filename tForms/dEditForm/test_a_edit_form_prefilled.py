import re
from playwright.sync_api import sync_playwright, expect
from utils.forms_helper import (
    open_browser, unique_form_title, create_form_api, question, delete_forms, goto, edit_url, main_content,
    open_title_editor, title_input, description_editor, question_cards, question_input, type_button,
    option_inputs, required_toggle, expect_toggle_on,
)


def test_edit_form_prefilled():
    """EF-001: the editor opens with the form's title, description, questions, types and options."""
    with sync_playwright() as p:
        browser, page = open_browser(p)
        title = unique_form_title()
        try:
            form = create_form_api(page, title, [
                question("Your name", required=True),
                question("Colour", "multiple_choice", ["Red", "Blue"]),
            ], description="<p>About the team</p>")
            goto(page, edit_url(form))
            main = main_content(page)

            expect(main.get_by_role("heading", name=f"Edit Form: {title}")).to_be_visible()
            expect(main.get_by_role("heading", name=title, exact=True)).to_be_visible()
            expect(main.get_by_text("About the team")).to_be_visible()

            open_title_editor(page)
            expect(title_input(page)).to_have_value(title)
            expect(description_editor(page)).to_have_text("About the team")

            cards = question_cards(page)
            expect(cards).to_have_count(2)
            expect(question_input(cards.nth(0))).to_have_value("Your name")
            expect(type_button(cards.nth(0))).to_have_text(re.compile("Short Answer"))
            expect_toggle_on(required_toggle(cards.nth(0)))
            expect(question_input(cards.nth(1))).to_have_value("Colour")
            expect(type_button(cards.nth(1))).to_have_text(re.compile("Multiple Choice"))
            assert [option_inputs(cards.nth(1)).nth(i).input_value() for i in range(2)] == ["Red", "Blue"]
            expect_toggle_on(required_toggle(cards.nth(1)), False)
        finally:
            delete_forms(page, title)

        browser.close()
