import re
from playwright.sync_api import sync_playwright, expect
from utils.forms_helper import (
    open_browser, open_my_forms, unique_form_title, create_form_api, delete_forms, search_forms, form_row,
    row_status_toggle, expect_row_active, expect_toast, status_filter, settle,
)


def test_toggle_status():
    """FM-011: the status switch deactivates a form and it shows under the Inactive filter."""
    with sync_playwright() as p:
        browser, page = open_browser(p)
        open_my_forms(page)
        title = unique_form_title()
        try:
            create_form_api(page, title)
            search_forms(page, title)
            row = form_row(page, title)
            expect_row_active(row)

            row_status_toggle(row).click()
            expect_toast(page, "Form status updated successfully.")
            expect_row_active(row, False)

            status_filter(page).select_option("inactive")
            expect(page).to_have_url(re.compile("status=inactive"))
            settle(page)
            expect(form_row(page, title)).to_have_count(1)
            expect_row_active(form_row(page, title), False)
        finally:
            delete_forms(page, title)

        browser.close()
