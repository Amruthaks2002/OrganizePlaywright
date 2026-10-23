from playwright.sync_api import sync_playwright, expect
from utils.app_releases_helper import (open_browser, page_props, reload_props, current_releases, restore_releases,
                                       open_edit_from_card, fill_form, save_button, submit, expect_toast, unique_tag,
                                       values, history_rows, open_notes, notes_dialog)


def test_save_in_place():
    """AR-035: saving an edit changes the current Android release in place: same release, no new History row, an
    Edited badge, and the new text in History and the release notes. The snapshot is restored afterwards (the
    release keeps its Edited badge)."""
    with sync_playwright() as p:
        browser, page = open_browser(p)
        snapshot = current_releases(page)
        before = page_props(page)
        old = snapshot["android"]
        message = f"AR-035 {unique_tag()}"
        try:
            open_edit_from_card(page, "android")
            fill_form(page, optional_message=message)
            submit(page, save_button(page), "Save changes")
            expect_toast(page, f"Android release {old['latest_version']} updated.")

            after = reload_props(page)
            new = after["current"]["android"]
            assert new["id"] == old["id"], new
            assert values(new) == {**values(old), "optional_message": message}, new
            assert new["edited"] is True, new
            assert after["history"]["total"] == before["history"]["total"]

            row = next(r for r in history_rows(page) if r["platform"] == "Android" and "Current" in r["badges"])
            assert row["badges"] == ["Current", "Edited"], row["badges"]
            assert row["optional"] == message, row
            open_notes(row)
            expect(notes_dialog(page).get_by_text(message)).to_be_visible()
        finally:
            restore_releases(page, snapshot)

        browser.close()
