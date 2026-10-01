import re
from playwright.sync_api import sync_playwright, expect
from utils.forms_helper import (
    open_browser, open_forms_submenu, main_content, title_input, description_editor, anonymous_button,
    header_button, save_button, question_cards, question_input, type_button, required_toggle, expect_toggle_on,
)


def test_page_loads():
    """CF-001: Forms > Create Form opens an empty form with one default Short Answer question."""
    with sync_playwright() as p:
        browser, page = open_browser(p)
        open_forms_submenu(page, "create-form")
        main = main_content(page)

        expect(page).to_have_url(re.compile(r"/forms/create$"))
        expect(main.get_by_role("heading", name="Create New Form")).to_be_visible()
        expect(anonymous_button(page)).to_be_enabled()
        expect(header_button(page, "Share")).to_be_disabled()
        expect(header_button(page, "Share")).to_have_attribute("title", "Save form to share")
        expect(header_button(page, "Preview")).to_be_disabled()
        expect(header_button(page, "Preview")).to_have_attribute("title", "Save form to preview")
        expect(header_button(page, "Settings")).to_be_enabled()
        expect(save_button(page)).to_be_enabled()

        expect(title_input(page)).to_have_value("")
        expect(description_editor(page)).to_have_text("")
        expect(question_cards(page)).to_have_count(1)
        card = question_cards(page).first
        expect(question_input(card)).to_have_value("Question 1")
        expect(type_button(card)).to_have_text(re.compile(r"Short Answer"))
        expect(card.get_by_placeholder("Enter answer")).to_be_visible()
        expect_toggle_on(required_toggle(card), False)

        browser.close()
