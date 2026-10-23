from playwright.sync_api import sync_playwright, expect
from utils.forms_helper import (
    open_browser, open_my_forms, unique_form_title, create_form_api, delete_forms, search_forms, form_row,
    row_status_toggle, expect_row_active, expect_toast, goto, submission_url, closed_page, submit_button, FORMS_URL,
)


def test_inactive_form_closed():
    """FM-012: an inactive form's public link shows "Form Closed"; reactivating it reopens the form."""
    with sync_playwright() as p:
        browser, page = open_browser(p)
        open_my_forms(page)
        title = unique_form_title()
        try:
            form = create_form_api(page, title)
            search_forms(page, title)
            row_status_toggle(form_row(page, title)).click()
            expect_toast(page, "Form status updated successfully.")
            expect_row_active(form_row(page, title), False)

            goto(page, submission_url(form))
            expect(page.get_by_role("heading", name="Form Closed")).to_be_visible()
            expect(closed_page(page, title)).to_be_visible()

            # the closed page has no sidebar
            goto(page, FORMS_URL)
            search_forms(page, title)
            row_status_toggle(form_row(page, title)).click()
            expect_toast(page, "Form status updated successfully.")
            expect_row_active(form_row(page, title))

            goto(page, submission_url(form))
            expect(page.get_by_role("heading", name=title)).to_be_visible()
            expect(submit_button(page)).to_have_text("Submit Form")
        finally:
            delete_forms(page, title)

        browser.close()
