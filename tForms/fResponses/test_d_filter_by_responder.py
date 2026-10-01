import re
from playwright.sync_api import sync_playwright, expect
from utils.forms_helper import (
    open_browser, unique_form_title, create_form_api, question, submit_response_api, delete_forms, goto,
    responses_url, responders_select, question_select, pick_option, responder_answer,
)


def test_filter_by_responder():
    """RS-004: picking a responder shows only their answers and locks the Question filter."""
    with sync_playwright() as p:
        browser, page = open_browser(p)
        title = unique_form_title()
        try:
            form = create_form_api(page, title, [question("Name"), question("Colour", "multiple_choice", ["Red", "Blue"])])
            submit_response_api(page, form, {"Name": "Sam", "Colour": "Blue"})
            goto(page, responses_url(form))

            responders_select(page).click()
            expect(page.get_by_role("option")).to_have_text(
                [re.compile(r"All Responders"), re.compile(r"Admin User\s*admin@example.com")])
            page.keyboard.press("Escape")

            pick_option(page, responders_select(page), "Admin User")
            expect(responders_select(page)).to_contain_text("Admin User")
            expect(question_select(page)).to_have_class(re.compile("vs--disabled"))
            expect(responder_answer(page, "Name")).to_have_text(re.compile(r"Name\s*Sam"))
            expect(responder_answer(page, "Colour")).to_have_text(re.compile(r"Colour\s*Blue"))
        finally:
            delete_forms(page, title)

        browser.close()
