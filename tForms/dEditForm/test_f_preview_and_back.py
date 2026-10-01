import re
from playwright.sync_api import sync_playwright, expect
from utils.forms_helper import (
    open_browser, unique_form_title, create_form_api, question, delete_forms, goto, edit_url, header_button,
    main_content,
)


def test_preview_and_back():
    """EF-005: Preview shows the form and Back to Editor returns to the editor."""
    with sync_playwright() as p:
        browser, page = open_browser(p)
        title = unique_form_title()
        try:
            form = create_form_api(page, title, [question("Your name")])
            goto(page, edit_url(form))
            main = main_content(page)

            header_button(page, "Preview").click()
            expect(page).to_have_url(re.compile(rf"/forms/{form['id']}$"))
            expect(main.get_by_role("heading", name=title)).to_be_visible()
            expect(main.locator("h3")).to_have_text(re.compile(r"1\. Your name"))

            main.get_by_role("button", name="Back to Editor").click()
            expect(page).to_have_url(re.compile(rf"/forms/{form['id']}/edit$"))
            expect(main.get_by_role("heading", name=f"Edit Form: {title}")).to_be_visible()
        finally:
            delete_forms(page, title)

        browser.close()
