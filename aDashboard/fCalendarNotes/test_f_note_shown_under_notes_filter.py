from playwright.sync_api import sync_playwright, expect
from utils.dashboard_helper import (open_browser_as, open_dashboard, add_note, go_to_month, note_event, chip_count,
                                    choose_chip, shown_events, calendar_events, month_cells, cleanup_notes, note_text,
                                    note_day)


def test_note_shown_under_notes_filter():
    """DB-043: a saved note shows on its date, is counted by the Notes chip and is listed under the Notes filter.

    The chip is compared with the notes listed in the same page load rather than with a count taken
    before saving, because tests running in parallel can add notes elsewhere in the month meanwhile."""
    day = note_day()
    text = note_text("filter")
    with sync_playwright() as p:
        browser, page = open_browser_as(p, "admin")
        try:
            add_note(page, day, text)

            open_dashboard(page)
            go_to_month(page, day)
            expect(note_event(page, day, text)).to_have_count(1)
            month_notes = calendar_events(month_cells(page), "note").count()
            assert chip_count(page, "NOTES") == month_notes, \
                f"Notes chip says {chip_count(page, 'NOTES')}, the month lists {month_notes} notes"

            choose_chip(page, "NOTES")
            expect(note_event(page, day, text)).to_be_visible()
            assert all("calendar-event-note" in e.get_attribute("class") for e in shown_events(page))
        finally:
            cleanup_notes(page, day, text)
            browser.close()
