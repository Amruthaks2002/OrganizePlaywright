from datetime import date
from playwright.sync_api import sync_playwright, expect
from utils.forms_helper import (
    open_browser, open_my_forms, unique_form_title, create_form_api, delete_forms, search_forms, form_row,
    expect_row_active, FORMS_URL,
)


def test_new_form_row():
    """FM-003: a new form is listed with its title, created date, Active status and actions."""
    with sync_playwright() as p:
        browser, page = open_browser(p)
        open_my_forms(page)
        title = unique_form_title()
        today = date.today()
        try:
            form = create_form_api(page, title)
            search_forms(page, title)
            row = form_row(page, title)

            expect(row).to_have_count(1)
            expect(row).to_contain_text(f"{today.day} {today.strftime('%b')}, {today.year}")
            expect(row).to_contain_text(today.strftime("%A"))
            expect_row_active(row)
            expect(row.get_by_role("link", name="View Response →")).to_have_attribute(
                "href", f"{FORMS_URL}/{form['id']}/responses")
            expect(row.get_by_title("Preview Form")).to_have_attribute("href", f"{FORMS_URL}/{form['id']}")
            expect(row.get_by_role("button", name="⋮")).to_be_visible()
        finally:
            delete_forms(page, title)

        browser.close()
