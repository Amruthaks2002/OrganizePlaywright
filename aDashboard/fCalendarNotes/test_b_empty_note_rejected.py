from playwright.sync_api import sync_playwright, expect
from utils.dashboard_helper import open_browser_as, open_day, day_notes, note_day, go_to_month


def test_empty_note_rejected():
    """DB-039: saving an empty note shows 'The note field is required.', keeps the dialog open and saves nothing."""
    with sync_playwright() as p:
        browser, page = open_browser_as(p, "admin")
        day = note_day()
        go_to_month(page, day)
        notes_before = day_notes(page, day)

        dialog = open_day(page, day)
        dialog.get_by_role("button", name="Save").click()
        expect(dialog.get_by_text("The note field is required.")).to_be_visible()
        expect(dialog).to_be_visible()
        dialog.get_by_role("button", name="Cancel").click()

        # only this day is compared: tests running in parallel add notes elsewhere in the month
        page.reload()
        go_to_month(page, day)
        assert day_notes(page, day) == notes_before
        browser.close()
