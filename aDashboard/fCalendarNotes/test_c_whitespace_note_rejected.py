import re

from playwright.sync_api import sync_playwright, expect
from utils.dashboard_helper import (open_browser_as, open_dashboard, open_day, day_notes, note_day, go_to_month,
                                    choose_chip, calendar_events, day_cell, modal, expect_toast)


def delete_blank_notes(page, day):
    """Deletes only notes with no visible text on day - never the day's other notes."""
    for _ in range(5):
        open_dashboard(page)
        go_to_month(page, day)
        choose_chip(page, "NOTES")
        blank = [e for e in calendar_events(day_cell(page, day), "note").all() if not e.text_content().strip()]
        if not blank:
            return
        blank[0].click()
        modal(page, "Edit Note").get_by_role("button", name="Delete").click()
        modal(page, "Delete Note").get_by_role("button", name="Delete").click()
        expect_toast(page, re.compile("Note deleted successfully", re.I))


def test_whitespace_note_rejected():
    """DB-040: a note made only of spaces is rejected like an empty one."""
    with sync_playwright() as p:
        browser, page = open_browser_as(p, "admin")
        day = note_day()
        go_to_month(page, day)
        notes_before = day_notes(page, day)
        try:
            dialog = open_day(page, day)
            dialog.locator("#note").fill("     ")
            dialog.get_by_role("button", name="Save").click()
            expect(dialog.get_by_text("The note field is required.")).to_be_visible()
            dialog.get_by_role("button", name="Cancel").click()

            # only this day is compared: tests running in parallel add notes elsewhere in the month
            page.reload()
            go_to_month(page, day)
            assert day_notes(page, day) == notes_before
        finally:
            if day_notes(page, day).count("") > notes_before.count(""):
                delete_blank_notes(page, day)
        browser.close()
