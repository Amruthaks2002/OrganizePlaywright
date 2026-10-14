from playwright.sync_api import sync_playwright
from utils.app_releases_helper import (open_browser, page_props, current_releases, restore_releases, publish_button,
                                       submit_expecting_error, assert_nothing_saved, bump)


def test_minimum_above_latest():
    """AR-024: a minimum higher than the latest is refused and nothing is saved (the confirmation still opens first)."""
    with sync_playwright() as p:
        browser, page = open_browser(p)
        snapshot = current_releases(page)
        total = page_props(page)["history"]["total"]
        release = snapshot["android"]
        try:
            for fields in [{"min_version": bump(release["latest_version"])}]:
                submit_expecting_error(page, publish_button(page), "min_version",
                                       "The minimum version cannot be higher than the latest version.",
                                       "android", **fields)
            assert_nothing_saved(page, snapshot, total)
        finally:
            restore_releases(page, snapshot)

        browser.close()
