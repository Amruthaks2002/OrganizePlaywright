from playwright.sync_api import sync_playwright, expect
from utils.forms_helper import (
    open_browser, unique_form_title, create_form_api, question, submit_response_api, delete_forms, goto,
    responses_url, analytics_card,
)


def test_analytics_view():
    """RS-002: Analytics lists text answers and charts choice questions."""
    with sync_playwright() as p:
        browser, page = open_browser(p)
        title = unique_form_title()
        try:
            form = create_form_api(page, title, [question("Name"), question("Colour", "multiple_choice", ["Red", "Blue"])])
            submit_response_api(page, form, {"Name": "Sam", "Colour": "Red"})
            submit_response_api(page, form, {"Name": "Alex", "Colour": "Blue"})
            goto(page, responses_url(form))

            expect(analytics_card(page, "Name")).to_contain_text("Sam")
            expect(analytics_card(page, "Name")).to_contain_text("Alex")
            expect(analytics_card(page, "Colour").locator("canvas")).to_be_visible()
        finally:
            delete_forms(page, title)

        browser.close()
