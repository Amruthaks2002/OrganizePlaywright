from datetime import date, timedelta
from playwright.sync_api import sync_playwright, expect
from utils.forms_helper import (
    open_browser, unique_form_title, create_form_api, delete_forms, goto, edit_url, header_button, share_dialog,
    dialog_setting,
)


def test_share_dialog_shows_settings():
    """EF-008: the share dialog shows the form's deadline, response limit and anonymity."""
    with sync_playwright() as p:
        browser, page = open_browser(p)
        title = unique_form_title()
        deadline = date.today() + timedelta(days=30)
        try:
            form = create_form_api(page, title, is_anonymous=True, stop_on_date=True,
                                   end_date=deadline.isoformat(), end_time="17:30",
                                   stop_on_limit=True, max_responses=5)
            goto(page, edit_url(form))

            header_button(page, "Share").click()
            dialog = share_dialog(page)
            expect(dialog_setting(dialog, "Stop accepting responses on")).not_to_have_text("No date set")
            expect(dialog_setting(dialog, "Stop accepting responses on")).to_contain_text(str(deadline.day))
            expect(dialog_setting(dialog, "Stop accepting responses after")).to_contain_text("5")
            expect(dialog_setting(dialog, "Anonymous responses")).to_have_text("Enabled")
        finally:
            delete_forms(page, title)

        browser.close()
