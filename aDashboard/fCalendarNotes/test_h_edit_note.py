import re

from playwright.sync_api import sync_playwright, expect
from utils.dashboard_helper import (open_browser_as, open_dashboard, add_note, open_note, go_to_month, note_event,
                                    cleanup_notes, expect_toast, note_text, note_day, ui_date)


def test_edit_note():
    """DB-045: clicking a note opens Edit Note with its text; saving a change updates that note only."""
    day = note_day()
    original, edited = note_text("before"), note_text("after")
    with sync_playwright() as p:
        browser, page = open_browser_as(p, "admin")
        try:
            add_note(page, day, original)
            open_dashboard(page)
            dialog = open_note(page, day, original)
            expect(dialog).to_contain_text(ui_date(day))
            expect(dialog.locator("#note")).to_have_value(original)
            dialog.locator("#note").fill(edited)
            dialog.get_by_role("button", name="Save").click()
            expect_toast(page, re.compile("note updated successfully", re.I))

            open_dashboard(page)
            go_to_month(page, day)
            expect(note_event(page, day, edited)).to_have_count(1)
            expect(note_event(page, day, original)).to_have_count(0)
        finally:
            cleanup_notes(page, day, original)
            cleanup_notes(page, day, edited)
            browser.close()
