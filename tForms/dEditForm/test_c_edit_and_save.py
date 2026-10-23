from playwright.sync_api import sync_playwright, expect
from utils.forms_helper import (
    open_browser, unique_form_title, create_form_api, question, delete_forms, goto, edit_url, open_title_editor,
    title_input, question_cards, question_input, save_button, expect_toast, FORMS_URL, search_forms, form_row,
    submission_url, public_form,
)


def test_edit_and_save():
    """EF-002: changing the title and a question and saving updates the list and the shared form."""
    with sync_playwright() as p:
        browser, page = open_browser(p)
        base = unique_form_title()
        try:
            form = create_form_api(page, f"{base} Before", [question("Old question")])
            goto(page, edit_url(form))

            open_title_editor(page)
            title_input(page).fill(f"{base} After")
            question_input(question_cards(page).first).fill("New question")
            save_button(page).click()
            expect_toast(page, "Form saved successfully.")

            goto(page, FORMS_URL)
            search_forms(page, base)
            expect(form_row(page, f"{base} After")).to_have_count(1)
            expect(form_row(page, f"{base} Before")).to_have_count(0)

            goto(page, submission_url(form))
            expect(page.get_by_role("heading", name=f"{base} After")).to_be_visible()
            expect(public_form(page).locator("h3")).to_have_text("1. New question")
        finally:
            delete_forms(page, base)

        browser.close()
