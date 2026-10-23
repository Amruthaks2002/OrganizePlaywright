from playwright.sync_api import sync_playwright, expect
from utils.dashboard_helper import (open_browser_as, open_dashboard, open_day, go_to_month, note_event, cleanup_notes,
                                    note_text, note_day)


def test_cancel_and_close_discard():
    """DB-042: Cancel and the X both close Add Note without saving what was typed."""
    day = note_day()
    text = note_text("discard")
    with sync_playwright() as p:
        browser, page = open_browser_as(p, "admin")
        try:
            for close in ["Cancel", "X"]:
                open_dashboard(page)
                dialog = open_day(page, day)
                dialog.locator("#note").fill(text)
                if close == "Cancel":
                    dialog.get_by_role("button", name="Cancel").click()
                else:
                    dialog.locator("button").first.click()
                expect(dialog).to_be_hidden()

            page.reload()
            go_to_month(page, day)
            expect(note_event(page, day, text)).to_have_count(0)
        finally:
            cleanup_notes(page, day, text)
            browser.close()
