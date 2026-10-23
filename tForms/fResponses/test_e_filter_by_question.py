from playwright.sync_api import sync_playwright, expect
from utils.forms_helper import (
    open_browser, unique_form_title, create_form_api, question, submit_response_api, delete_forms, goto,
    responses_url, question_select, pick_option, analytics_card,
)


def test_filter_by_question():
    """RS-005: picking a question shows only that question's results."""
    with sync_playwright() as p:
        browser, page = open_browser(p)
        title = unique_form_title()
        try:
            form = create_form_api(page, title, [question("Name"), question("Team")])
            submit_response_api(page, form, {"Name": "Sam", "Team": "QA"})
            goto(page, responses_url(form))

            question_select(page).click()
            expect(page.get_by_role("option")).to_have_text(["All Question", "Name", "Team"])
            page.keyboard.press("Escape")

            pick_option(page, question_select(page), "Team")
            expect(analytics_card(page, "Team")).to_contain_text("QA")
            expect(analytics_card(page, "Name")).to_have_count(0)
        finally:
            delete_forms(page, title)

        browser.close()
