from playwright.sync_api import sync_playwright, expect
from utils.forms_helper import (
    open_browser, open_create_form, unique_form_title, delete_forms, build_form, save_new_form, goto,
    submission_url, public_question, TYPE_KEYS,
)


def test_all_types_on_public_form():
    """CF-015: a form using all seven question types renders each one correctly when shared."""
    with sync_playwright() as p:
        browser, page = open_browser(p)
        open_create_form(page)
        title = unique_form_title()
        try:
            build_form(page, title, [
                ("Short q", "Short Answer", (), False),
                ("Paragraph q", "Paragraph", (), False),
                ("Choice q", "Multiple Choice", ("M1", "M2"), False),
                ("Check q", "Check Box", ("C1", "C2"), False),
                ("Drop q", "Drop-down", ("D1", "D2"), False),
                ("Date q", "Date", (), False),
                ("Time q", "Time", (), False),
            ])
            form = save_new_form(page)
            assert [f["type"] for f in form["fields"]] == list(TYPE_KEYS.values())

            goto(page, submission_url(form))
            expect(public_question(page, "Short q").locator("input[type=text]")).to_be_visible()
            expect(public_question(page, "Paragraph q").locator("textarea")).to_be_visible()
            expect(public_question(page, "Choice q").locator("label:has(input[type=radio])")).to_have_text(["M1", "M2"])
            expect(public_question(page, "Check q").locator("label:has(input[type=checkbox])")).to_have_text(["C1", "C2"])
            public_question(page, "Drop q").locator(".v-select").click()
            expect(page.get_by_role("option")).to_have_text(["D1", "D2"])
            page.keyboard.press("Escape")
            expect(public_question(page, "Date q").locator("input[type=date]")).to_be_visible()
            expect(public_question(page, "Time q").locator("input[type=time]")).to_be_visible()
        finally:
            delete_forms(page, title)

        browser.close()
