from playwright.sync_api import sync_playwright
from utils.app_releases_helper import (open_browser, page_props, reload_props, current_releases, restore_releases,
                                       publish, expect_toast, unique_tag, values, card_values)


def test_whitespace_trimmed():
    """AR-018: spaces around the versions and messages are dropped when a release is published.
    The snapshot is restored afterwards."""
    with sync_playwright() as p:
        browser, page = open_browser(p)
        snapshot = current_releases(page)
        old = page_props(page)["current"]["android"]
        message = f"AR-018 {unique_tag()}"
        try:
            publish(page, "android", latest_version=f"  {old['latest_version']}  ",
                    min_version=f" {old['min_version']} ", optional_message=f"  {message}  ")
            expect_toast(page, f"Android release {old['latest_version']} published.")

            new = reload_props(page)["current"]["android"]
            assert new["id"] != old["id"], new
            assert values(new) == {**values(old), "optional_message": message}, new
            assert card_values(page, "android")["latest"] == old["latest_version"]
        finally:
            restore_releases(page, snapshot)

        browser.close()
