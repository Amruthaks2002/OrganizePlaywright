from playwright.sync_api import sync_playwright, expect
from utils.forms_helper import (
    open_browser, unique_form_title, create_form_api, question, delete_forms, goto, submission_url,
    public_question, answer_input, submit_button, thank_you, responses_url, view_tab, table_rows,
    responses_table,
)


def test_edit_response():
    """SB-006: with response editing on, the earlier answers come back prefilled and can be updated."""
    with sync_playwright() as p:
        browser, page = open_browser(p)
        title = unique_form_title()
        try:
            form = create_form_api(page, title, [question("Name"), question("Colour", "multiple_choice", ["Red", "Blue"])],
                                   allow_editing=True)
            goto(page, submission_url(form))
            answer_input(page, "Name").fill("Sam")
            public_question(page, "Colour").get_by_label("Red").check()
            submit_button(page).click()
            expect(thank_you(page)).to_be_visible()
            expect(page.get_by_role("button", name="Edit your response")).to_be_visible()

            goto(page, submission_url(form))
            expect(answer_input(page, "Name")).to_have_value("Sam")
            expect(public_question(page, "Colour").get_by_label("Red")).to_be_checked()
            expect(submit_button(page)).to_have_text("Update Form")

            answer_input(page, "Name").fill("Sam Edited")
            public_question(page, "Colour").get_by_label("Blue").check()
            submit_button(page).click()
            expect(thank_you(page)).to_be_visible()

            goto(page, responses_url(form))
            view_tab(page, "Tabular").click()
            expect(responses_table(page)).to_be_visible()
            rows = table_rows(page)
            assert len(rows) == 1, rows
            assert rows[0][2:] == ["Sam Edited", "Blue"], rows
        finally:
            delete_forms(page, title)

        browser.close()
