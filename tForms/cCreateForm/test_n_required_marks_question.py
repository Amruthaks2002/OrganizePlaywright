from playwright.sync_api import sync_playwright, expect
from utils.forms_helper import (
    open_browser, open_create_form, unique_form_title, delete_forms, build_form, save_new_form, goto,
    submission_url, public_question,
)


def test_required_marks_question():
    """CF-014: Is Required puts a * on the question in the public form."""
    with sync_playwright() as p:
        browser, page = open_browser(p)
        open_create_form(page)
        title = unique_form_title()
        try:
            build_form(page, title, [("Mandatory question", "Short Answer", (), True),
                                     ("Optional question", "Short Answer", (), False)])
            form = save_new_form(page)
            assert [f["validation"]["required"] for f in form["fields"]] == [True, False]

            goto(page, submission_url(form))
            expect(public_question(page, "Mandatory question").locator("h3 span.text-red-500")).to_have_text("*")
            expect(public_question(page, "Optional question").locator("h3 span.text-red-500")).to_have_count(0)
        finally:
            delete_forms(page, title)

        browser.close()
