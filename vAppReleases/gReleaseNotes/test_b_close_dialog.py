from playwright.sync_api import sync_playwright, expect
from utils.app_releases_helper import open_browser, open_releases, history_rows, open_notes, notes_dialog


def test_close_dialog():
    """AR-039: the release notes close with the Close button and with Esc."""
    with sync_playwright() as p:
        browser, page = open_browser(p)
        open_releases(page)
        row = next(r for r in history_rows(page) if r["has_notes"])

        for close in [lambda: notes_dialog(page).get_by_role("button", name="Close").last.click(),
                      lambda: page.keyboard.press("Escape")]:
            open_notes(row)
            expect(notes_dialog(page)).to_be_visible()
            close()
            expect(notes_dialog(page)).to_have_count(0)

        browser.close()
