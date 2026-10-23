from playwright.sync_api import sync_playwright
from utils.app_releases_helper import (open_browser, open_releases, page_props, reload_props, current_releases,
                                       restore_releases, publish, expect_toast, unique_tag, card_values, current_row,
                                       visible_row)


def ios_current_row(page):
    return visible_row(current_row(page, "ios"))


def test_other_platform_unaffected():
    """AR-015: publishing for Android leaves the iOS card and the iOS Current row as they were.
    The snapshot is restored afterwards."""
    with sync_playwright() as p:
        browser, page = open_browser(p)
        snapshot = current_releases(page)
        old = page_props(page)["current"]["android"]
        ios_card = card_values(page, "ios")
        ios_row = ios_current_row(page)
        open_releases(page)
        try:
            publish(page, "android", optional_message=f"AR-015 {unique_tag()}")
            expect_toast(page, f"Android release {old['latest_version']} published.")

            assert reload_props(page)["current"]["ios"] == snapshot["ios"]
            assert card_values(page, "ios") == ios_card
            assert ios_current_row(page) == ios_row
        finally:
            restore_releases(page, snapshot)

        browser.close()
