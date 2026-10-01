from playwright.sync_api import sync_playwright, expect
from utils.forms_helper import (
    open_browser, unique_form_title, create_form_api, question, delete_forms, goto, submission_url, public_form,
    submit_button,
)


def test_public_form_layout():
    """SB-001: the shared form shows its title, description, numbered questions, Clear Form and Submit Form."""
    with sync_playwright() as p:
        browser, page = open_browser(p)
        title = unique_form_title()
        try:
            form = create_form_api(page, title, [question("Your name"), question("Your team")],
                                   description="<p>Tell us about you</p>")
            goto(page, submission_url(form))

            expect(page.get_by_role("heading", name=title, level=1)).to_be_visible()
            expect(page.get_by_text("Tell us about you")).to_be_visible()
            expect(public_form(page).locator("h3")).to_have_text(["1. Your name", "2. Your team"])
            expect(public_form(page).get_by_role("button", name="Clear Form")).to_be_visible()
            expect(submit_button(page)).to_have_text("Submit Form")
            expect(submit_button(page)).to_be_enabled()
        finally:
            delete_forms(page, title)

        browser.close()
