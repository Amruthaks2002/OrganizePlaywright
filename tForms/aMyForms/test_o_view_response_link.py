import re
from playwright.sync_api import sync_playwright, expect
from utils.forms_helper import (
    open_browser, open_my_forms, unique_form_title, create_form_api, delete_forms, search_forms, form_row,
    main_content,
)


def test_view_response_link():
    """FM-015: View Response opens the form's responses page."""
    with sync_playwright() as p:
        browser, page = open_browser(p)
        open_my_forms(page)
        title = unique_form_title()
        try:
            form = create_form_api(page, title)
            search_forms(page, title)

            form_row(page, title).get_by_role("link", name="View Response →").click()
            expect(page).to_have_url(re.compile(rf"/forms/{form['id']}/responses$"))
            expect(main_content(page).get_by_role("heading", name=title)).to_be_visible()
            expect(main_content(page).get_by_text("No responses yet")).to_be_visible()
        finally:
            delete_forms(page, title)

        browser.close()
