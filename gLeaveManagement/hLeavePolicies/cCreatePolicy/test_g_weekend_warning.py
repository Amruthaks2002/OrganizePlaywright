from playwright.sync_api import sync_playwright, expect
from utils.leave_policy_helper import open_browser, open_leave_policies, open_create_form, weekend_checkbox


def test_weekend_warning():
    """LP-021: the 'no weekends' warning hides when a day is ticked and returns when all are unticked."""
    with sync_playwright() as p:
        browser, page = open_browser(p)
        open_leave_policies(page)

        form = open_create_form(page)
        warning = form.get_by_text("No weekends selected. All days will be treated as working days.")
        expect(warning).to_be_visible()

        weekend_checkbox(form, "Saturday").check()
        expect(warning).to_be_hidden()
        weekend_checkbox(form, "Sunday").check()
        expect(warning).to_be_hidden()

        weekend_checkbox(form, "Saturday").uncheck()
        expect(warning).to_be_hidden()
        weekend_checkbox(form, "Sunday").uncheck()
        expect(warning).to_be_visible()

        browser.close()
