from playwright.sync_api import sync_playwright
from utils.forms_helper import (
    open_browser, open_probation_reviews, unique_form_title, create_form_api, delete_forms, search_forms,
    form_row, row_status_toggle, expect_row_active, expect_toast,
)


def test_toggle_status():
    """PR-004: the status switch works on the probation list."""
    with sync_playwright() as p:
        browser, page = open_browser(p)
        open_probation_reviews(page)
        title = unique_form_title()
        try:
            create_form_api(page, title, type="probation_review")
            search_forms(page, title)
            row = form_row(page, title)
            expect_row_active(row)

            row_status_toggle(row).click()
            expect_toast(page, "Form status updated successfully.")
            expect_row_active(row, False)

            search_forms(page, title)
            expect_row_active(form_row(page, title), False)
        finally:
            delete_forms(page, title)

        browser.close()
