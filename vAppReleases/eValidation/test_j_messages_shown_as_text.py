from playwright.sync_api import sync_playwright, expect
from utils.app_releases_helper import (open_browser, current_releases, restore_releases, publish, expect_toast,
                                       reload_props, unique_tag, history_rows, open_notes, notes_dialog)


def test_messages_shown_as_text():
    """AR-029: HTML in an update message is shown as plain text in History and in the release notes, and never
    runs. The snapshot is restored afterwards."""
    with sync_playwright() as p:
        browser, page = open_browser(p)
        snapshot = current_releases(page)
        message = f'<b>AR-029 {unique_tag()}</b><img src=x onerror="window.__ar029=1">'
        try:
            publish(page, "android", optional_message=message)
            expect_toast(page, f"Android release {snapshot['android']['latest_version']} published.")

            assert reload_props(page)["current"]["android"]["optional_message"] == message
            top = history_rows(page)[0]
            assert top["optional"] == message, top
            assert top["row"].locator("td").nth(4).locator("b, img").count() == 0
            open_notes(top)
            expect(notes_dialog(page).get_by_text(message)).to_be_visible()
            assert notes_dialog(page).locator("b, img").count() == 0
            assert page.evaluate("window.__ar029") is None
        finally:
            restore_releases(page, snapshot)

        browser.close()
