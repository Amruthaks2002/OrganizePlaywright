import datetime
import re

from playwright.sync_api import sync_playwright, expect
from utils.dashboard_helper import (open_browser_as, open_dashboard, add_note, cleanup_notes, go_to_month, day_cell,
                                    calendar_events, modal, note_text, note_day, ui_date, number)


def test_more_events_popup():
    """DB-033: a day with more items than fit shows '+N more'; clicking it opens an Events popup for
    that date listing every item with its type, and Close dismisses it."""
    # two days after the note tests' day, so the note tests running in parallel never share this cell
    day = note_day() + datetime.timedelta(days=2)
    notes = [note_text(f"more {i}") for i in range(3)]
    tag = notes[0].rsplit(" ", 1)[1]
    with sync_playwright() as p:
        browser, page = open_browser_as(p, "admin")
        try:
            for note in notes:
                open_dashboard(page)
                add_note(page, day, note)
            open_dashboard(page)
            go_to_month(page, day)
            cell = day_cell(page, day)
            more = cell.locator("a.fc-more-link")
            expect(more).to_be_visible()
            total = len([e for e in calendar_events(cell).all() if e.is_visible()]) + number(more.inner_text())

            more.click()
            popup = modal(page, "Events")
            expect(popup).to_contain_text(ui_date(day))
            expect(popup.get_by_text(str(total), exact=True)).to_be_visible()
            for note in notes:
                expect(popup.get_by_text(note)).to_be_visible()
            expect(popup.get_by_text(re.compile(r"^\s*note\s*$", re.I))).to_have_count(3)
            popup.get_by_role("button", name="Close").click()
            expect(popup).to_be_hidden()
        finally:
            for note in notes:
                cleanup_notes(page, day, note)
            browser.close()
