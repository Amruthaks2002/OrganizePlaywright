from playwright.sync_api import sync_playwright, expect
from utils.forms_helper import (
    open_browser, unique_form_title, create_form_api, question, submit_response_api, delete_forms, goto,
    submission_url, MY_SUBMISSIONS_URL, submission_row, submit_button,
)


def test_view_submission():
    """MS-003: View opens the submitted form."""
    with sync_playwright() as p:
        browser, page = open_browser(p)
        title = unique_form_title()
        try:
            form = create_form_api(page, title, [question("Name")])
            submit_response_api(page, form, {"Name": "Sam"})
            goto(page, MY_SUBMISSIONS_URL)

            submission_row(page, title).get_by_role("link", name="View").click()
            expect(page).to_have_url(submission_url(form))
            expect(page.get_by_role("heading", name=title)).to_be_visible()
            expect(submit_button(page)).to_have_text("Cannot Edit Response")
        finally:
            delete_forms(page, title)

        browser.close()
