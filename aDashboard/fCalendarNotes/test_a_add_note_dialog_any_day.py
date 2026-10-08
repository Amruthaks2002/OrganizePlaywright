import datetime

from playwright.sync_api import sync_playwright, expect
from utils.dashboard_helper import open_browser_as, open_dashboard, open_day, ui_date, today


def test_add_note_dialog_any_day():
    """DB-038: clicking a date opens Add Note for that date - today, a past date and a future date."""
    with sync_playwright() as p:
        browser, page = open_browser_as(p, "admin")
        for day in [today(), today() - datetime.timedelta(days=3), today() + datetime.timedelta(days=3)]:
            open_dashboard(page)
            dialog = open_day(page, day)
            expect(dialog).to_contain_text(ui_date(day))
            expect(dialog.locator("#note")).to_have_value("")
            expect(dialog.locator("#note")).to_have_attribute("placeholder", "What's on your mind...")
            dialog.get_by_role("button", name="Cancel").click()
            expect(dialog).to_be_hidden()
        browser.close()
