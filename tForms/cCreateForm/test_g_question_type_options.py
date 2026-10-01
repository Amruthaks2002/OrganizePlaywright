from playwright.sync_api import sync_playwright, expect
from utils.forms_helper import open_browser, open_create_form, question_cards, type_button, type_menu, QUESTION_TYPES


def test_question_type_options():
    """CF-007: the Type dropdown lists all seven question types."""
    with sync_playwright() as p:
        browser, page = open_browser(p)
        open_create_form(page)
        card = question_cards(page).first

        type_button(card).click()
        expect(type_menu(card).locator("button span.flex-1")).to_have_text(QUESTION_TYPES)

        browser.close()
