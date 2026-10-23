import pytest
from playwright.sync_api import sync_playwright, expect
from utils.forms_helper import open_browser, open_create_form, question_cards, set_question_type, option_inputs

PREVIEWS = {
    "Short Answer": "input[placeholder='Enter answer']",
    "Paragraph": "textarea[placeholder='Enter long answer']",
    "Multiple Choice": "input[placeholder='Add the option here']",
    "Check Box": "input[placeholder='Add the option here']",
    "Drop-down": "input[placeholder='Add the option here']",
    "Date": "input[placeholder='12 March 2026']",
    "Time": "input[placeholder='10:00 AM']",
}


@pytest.mark.parametrize("type_name", list(PREVIEWS))
def test_question_type_preview(type_name):
    """CF-008: each question type shows its own answer preview."""
    with sync_playwright() as p:
        browser, page = open_browser(p)
        open_create_form(page)
        card = question_cards(page).first

        if type_name != "Short Answer":
            set_question_type(card, type_name)
        expect(card.locator(PREVIEWS[type_name])).to_be_visible()

        if type_name in ("Multiple Choice", "Check Box", "Drop-down"):
            expect(option_inputs(card)).to_have_count(1)
            expect(card.get_by_role("button", name="Add Option")).to_be_visible()
        else:
            expect(option_inputs(card)).to_have_count(0)
        if type_name == "Date":
            expect(card.get_by_text("Select Date")).to_be_visible()
        if type_name == "Time":
            expect(card.get_by_text("Select Time")).to_be_visible()

        browser.close()
