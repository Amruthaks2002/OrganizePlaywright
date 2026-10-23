from playwright.sync_api import sync_playwright, expect
from utils.app_releases_helper import (open_browser, current_releases, restore_releases, reload_props,
                                       open_edit_from_card, fill_form, save_button, submit, expect_toast, unique_tag,
                                       history_rows, open_notes, notes_dialog)


def test_long_message():
    """AR-041: a 500-character message is cut to one line in History and shown in full in the release notes.
    Set with an in-place edit of the current Android release (no new row); the snapshot is restored afterwards."""
    with sync_playwright() as p:
        browser, page = open_browser(p)
        snapshot = current_releases(page)
        start = f"AR-041 {unique_tag()} "
        message = start + "long message " * 40
        message = message[:500]
        try:
            open_edit_from_card(page, "android")
            fill_form(page, optional_message=message)
            submit(page, save_button(page), "Save changes")
            expect_toast(page, f"Android release {snapshot['android']['latest_version']} updated.")
            assert reload_props(page)["current"]["android"]["optional_message"] == message

            row = next(r for r in history_rows(page) if r["platform"] == "Android" and "Current" in r["badges"])
            cell = row["row"].locator("td").nth(4).locator("p").first
            expect(cell).to_have_class("line-clamp-1")
            line_height = cell.evaluate("e => parseFloat(getComputedStyle(e).lineHeight)")
            assert cell.bounding_box()["height"] <= line_height + 1, (cell.bounding_box(), line_height)

            open_notes(row)
            expect(notes_dialog(page).get_by_text(message, exact=True)).to_be_visible()
        finally:
            restore_releases(page, snapshot)

        browser.close()
