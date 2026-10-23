import re

from playwright.sync_api import sync_playwright, expect
from utils.dashboard_helper import (open_browser_as, open_dashboard, add_note, open_note, go_to_month, note_event, modal,
                                    cleanup_notes, expect_toast, note_text, note_day)


def test_delete_note_confirmation():
    """DB-046: Delete asks for confirmation; Cancel keeps the note and confirming removes it."""
    day = note_day()
    text = note_text("delete")
    with sync_playwright() as p:
        browser, page = open_browser_as(p, "admin")
        try:
            add_note(page, day, text)
            open_dashboard(page)
            open_note(page, day, text).get_by_role("button", name="Delete").click()
            confirm = modal(page, "Delete Note")
            expect(confirm).to_contain_text("Are you sure you want to delete this note? This action cannot be undone.")
            confirm.get_by_role("button", name="Cancel").click()
            expect(confirm).to_be_hidden()

            open_dashboard(page)
            go_to_month(page, day)
            expect(note_event(page, day, text)).to_have_count(1)

            open_note(page, day, text).get_by_role("button", name="Delete").click()
            modal(page, "Delete Note").get_by_role("button", name="Delete").click()
            expect_toast(page, re.compile("Note deleted successfully", re.I))
            open_dashboard(page)
            go_to_month(page, day)
            expect(note_event(page, day, text)).to_have_count(0)
        finally:
            cleanup_notes(page, day, text)
            browser.close()
