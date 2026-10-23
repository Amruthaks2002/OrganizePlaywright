from playwright.sync_api import sync_playwright, expect
from utils.app_releases_helper import (open_browser, page_props, reload_props, current_releases, restore_releases,
                                       fill_form, publish_button, confirm_dialog, dialog_message, is_release_request,
                                       expect_toast, card_values, raised_min)


def test_raise_minimum():
    """AR-016: publishing a higher minimum warns which installs get blocked, then saves it.
    The new minimum stays at or below the latest, so no install on the latest version is blocked; the snapshot is
    restored afterwards."""
    with sync_playwright() as p:
        browser, page = open_browser(p)
        snapshot = current_releases(page)
        old = page_props(page)["current"]["android"]
        latest, minimum = old["latest_version"], raised_min(old)
        try:
            fill_form(page, "android", latest_version=latest, min_version=minimum)
            publish_button(page).click()
            expect(dialog_message(page)).to_have_text(
                f"Latest {latest}, minimum {minimum}. Installs below {minimum} will be blocked until they update.")
            with page.expect_response(lambda r: is_release_request(r.request)):
                confirm_dialog(page).get_by_role("button", name="Publish", exact=True).click()
            expect_toast(page, f"Android release {latest} published.")

            assert reload_props(page)["current"]["android"]["min_version"] == minimum
            assert card_values(page, "android")["min"] == minimum
        finally:
            restore_releases(page, snapshot)

        browser.close()
