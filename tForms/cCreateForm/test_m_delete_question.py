from playwright.sync_api import sync_playwright, expect
from utils.forms_helper import open_browser, open_create_form, question_cards, question_input, add_question


def test_delete_question():
    """CF-013: the Delete icon removes that question."""
    with sync_playwright() as p:
        browser, page = open_browser(p)
        open_create_form(page)
        question_input(question_cards(page).first).fill("Remove me")
        question_input(add_question(page)).fill("Keep me")

        question_cards(page).first.get_by_title("Delete").click()
        expect(question_cards(page)).to_have_count(1)
        expect(question_input(question_cards(page).first)).to_have_value("Keep me")

        browser.close()
