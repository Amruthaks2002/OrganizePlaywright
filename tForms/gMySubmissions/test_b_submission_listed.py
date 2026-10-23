import re
from datetime import date
from playwright.sync_api import sync_playwright, expect
from utils.forms_helper import (
    open_browser, unique_form_title, create_form_api, question, delete_forms, goto, submission_url,
    answer_input, submit_button, thank_you, open_my_submissions, submission_row, BASE_URL,
)


def test_submission_listed():
    """MS-002: a submitted form is listed with its submission date, weekday and time."""
    with sync_playwright() as p:
        browser, page = open_browser(p)
        title = unique_form_title()
        today = date.today()
        try:
            form = create_form_api(page, title, [question("Name")])
            goto(page, submission_url(form))
            answer_input(page, "Name").fill("Sam")
            submit_button(page).click()
            expect(thank_you(page)).to_be_visible()

            goto(page, f"{BASE_URL}/dashboard")
            open_my_submissions(page)
            row = submission_row(page, title)
            expect(row).to_have_count(1)
            expect(row).to_contain_text(f"{today.day} {today.strftime('%b')}, {today.year}")
            expect(row).to_contain_text(today.strftime("%A"))
            expect(row.locator("p").nth(2)).to_have_text(re.compile(r"\d{1,2}:\d{2} (AM|PM)"))
        finally:
            delete_forms(page, title)

        browser.close()
