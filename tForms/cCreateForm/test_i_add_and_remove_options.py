import re
from playwright.sync_api import sync_playwright, expect
from utils.forms_helper import open_browser, open_create_form, question_cards, set_question_type, option_inputs


def test_add_and_remove_options():
    """CF-009: Add Option adds an option row and × removes one."""
    with sync_playwright() as p:
        browser, page = open_browser(p)
        open_create_form(page)
        card = question_cards(page).first
        set_question_type(card, "Multiple Choice")

        option_inputs(card).nth(0).fill("Red")
        card.get_by_role("button", name="Add Option").click()
        option_inputs(card).nth(1).fill("Green")
        card.get_by_role("button", name="Add Option").click()
        option_inputs(card).nth(2).fill("Blue")
        expect(option_inputs(card)).to_have_count(3)
        expect(card.locator("label").filter(has_text=re.compile(r"^\s*Option \d+\s*$"))).to_have_text(
            [re.compile(r"Option 1"), re.compile(r"Option 2"), re.compile(r"Option 3"), re.compile(r"Option 4")])

        # remove the middle option
        card.get_by_role("button", name="×").nth(1).click()
        expect(option_inputs(card)).to_have_count(2)
        assert [option_inputs(card).nth(i).input_value() for i in range(2)] == ["Red", "Blue"]

        browser.close()
