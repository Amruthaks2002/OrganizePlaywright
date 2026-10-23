from playwright.sync_api import sync_playwright
from utils.app_releases_helper import (open_browser, page_props, reload_props, current_releases, restore_releases,
                                       publish, expect_toast, history_rows)


def test_publish_default_messages():
    """AR-014: a release published with both messages empty stores none, and History shows 'Optional: Default' /
    'Mandatory: Default' with no View release notes button. The snapshot is restored afterwards."""
    with sync_playwright() as p:
        browser, page = open_browser(p)
        snapshot = current_releases(page)
        old = page_props(page)["current"]["android"]
        try:
            publish(page, "android", latest_version=old["latest_version"], min_version=old["min_version"],
                    optional_message="", mandatory_message="")
            expect_toast(page, f"Android release {old['latest_version']} published.")

            new = reload_props(page)["current"]["android"]
            assert new["id"] != old["id"], new
            assert (new["optional_message"], new["mandatory_message"]) == (None, None), new
            top = history_rows(page)[0]
            assert (top["platform"], top["optional"], top["mandatory"], top["has_notes"]) == \
                ("Android", "Default", "Default", False), top
        finally:
            restore_releases(page, snapshot)

        browser.close()
