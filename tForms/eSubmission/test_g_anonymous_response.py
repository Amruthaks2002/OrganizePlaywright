from playwright.sync_api import sync_playwright, expect
from utils.forms_helper import (
    open_browser, unique_form_title, create_form_api, question, delete_forms, goto, submission_url,
    answer_input, submit_button, thank_you, responses_url, view_tab, responses_table, table_rows,
    MY_SUBMISSIONS_URL, submission_row,
)


def test_anonymous_response():
    """SB-007: responses to an anonymous form show as "Anonymous" and aren't listed in My Submissions."""
    with sync_playwright() as p:
        browser, page = open_browser(p)
        title = unique_form_title()
        try:
            form = create_form_api(page, title, [question("Feedback")], is_anonymous=True)
            goto(page, submission_url(form))
            answer_input(page, "Feedback").fill("Secret note")
            submit_button(page).click()
            expect(thank_you(page)).to_be_visible()

            goto(page, responses_url(form))
            view_tab(page, "Tabular").click()
            expect(responses_table(page)).to_be_visible()
            assert [row[1:] for row in table_rows(page)] == [["Anonymous", "Secret note"]]

            goto(page, MY_SUBMISSIONS_URL)
            expect(submission_row(page, title)).to_have_count(0)
        finally:
            delete_forms(page, title)

        browser.close()
