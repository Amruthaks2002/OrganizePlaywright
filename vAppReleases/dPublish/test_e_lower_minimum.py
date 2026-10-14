from playwright.sync_api import sync_playwright, expect
from utils.app_releases_helper import (open_browser, page_props, reload_props, current_releases, restore_releases,
                                       fill_form, publish_button, confirm_dialog, is_release_request, expect_toast,
                                       card_values, lower)


def test_lower_minimum():
    """AR-017: a lower minimum is published through the 'Lower minimum' confirmation.
    The snapshot is restored afterwards."""
    with sync_playwright() as p:
        browser, page = open_browser(p)
        snapshot = current_releases(page)
        old = page_props(page)["current"]["android"]
        minimum = lower(old["min_version"])
        try:
            fill_form(page, "android", min_version=minimum)
            publish_button(page).click()
            expect(confirm_dialog(page)).to_be_visible()
            with page.expect_response(lambda r: is_release_request(r.request)):
                confirm_dialog(page).get_by_role("button", name="Lower minimum", exact=True).click()
            expect_toast(page, f"Android release {old['latest_version']} published.")

            assert reload_props(page)["current"]["android"]["min_version"] == minimum
            assert card_values(page, "android")["min"] == minimum
        finally:
            restore_releases(page, snapshot)

        browser.close()
