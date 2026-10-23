from playwright.sync_api import sync_playwright, expect
from utils.dashboard_helper import (open_browser_as, add_note, go_to_month, note_event, next_month, prev_month,
                                    cleanup_notes, note_text, note_day)


def test_note_persists():
    """DB-047: a saved note is still there after reloading the page and after moving away from its month and back."""
    day = note_day()
    text = note_text("persist")
    with sync_playwright() as p:
        browser, page = open_browser_as(p, "admin")
        try:
            add_note(page, day, text)
            page.reload()
            go_to_month(page, day)
            expect(note_event(page, day, text)).to_have_count(1)

            next_month(page)
            prev_month(page)
            prev_month(page)
            go_to_month(page, day)
            expect(note_event(page, day, text)).to_have_count(1)
        finally:
            cleanup_notes(page, day, text)
            browser.close()
