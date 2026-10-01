from datetime import date
from playwright.sync_api import sync_playwright, expect
from utils.forms_helper import (
    open_browser, unique_form_title, create_form_api, delete_forms, goto, edit_url, open_settings,
    settings_toggle, expect_toast, submission_url, closed_page,
)


def test_deadline_closes_form():
    """EF-007: once the "On a date" deadline has passed the form shows "Form Closed".

    Dates before today are rejected, so the deadline is today at 00:01.
    """
    with sync_playwright() as p:
        browser, page = open_browser(p)
        title = unique_form_title()
        try:
            form = create_form_api(page, title)
            goto(page, edit_url(form))
            panel = open_settings(page)
            settings_toggle(panel, "On a date").click()
            panel.locator("input[type=date]").fill(date.today().isoformat())
            panel.locator("input[type=time]").fill("00:01")
            panel.get_by_role("button", name="Save").click()
            expect_toast(page, "Form saved successfully.")

            goto(page, submission_url(form))
            expect(page.get_by_role("heading", name="Form Closed")).to_be_visible()
            expect(closed_page(page, title)).to_be_visible()
        finally:
            delete_forms(page, title)

        browser.close()
