from playwright.sync_api import sync_playwright, expect
from utils.forms_helper import (
    open_browser, unique_form_title, create_form_api, question, submit_response_api, delete_forms, goto,
    responses_url, responders_select, question_select, pick_option, analytics_card,
)


def test_clear_filters():
    """RS-006: the ✕ on a filter brings back "All Responders" / "All Question"."""
    with sync_playwright() as p:
        browser, page = open_browser(p)
        title = unique_form_title()
        try:
            form = create_form_api(page, title, [question("Name"), question("Team")])
            submit_response_api(page, form, {"Name": "Sam", "Team": "QA"})
            goto(page, responses_url(form))

            pick_option(page, question_select(page), "Team")
            expect(analytics_card(page, "Name")).to_have_count(0)
            question_select(page).get_by_role("button", name="Clear Selected").click()
            expect(question_select(page)).to_contain_text("All Question")
            expect(analytics_card(page, "Name")).to_be_visible()

            pick_option(page, responders_select(page), "Admin User")
            responders_select(page).get_by_role("button", name="Clear Selected").click()
            expect(responders_select(page)).to_contain_text("All Responders")
        finally:
            delete_forms(page, title)

        browser.close()
