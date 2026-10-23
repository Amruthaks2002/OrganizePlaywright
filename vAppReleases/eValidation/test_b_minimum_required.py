from playwright.sync_api import sync_playwright
from utils.app_releases_helper import (open_browser, page_props, current_releases, restore_releases, publish_button,
                                       submit_expecting_error, assert_nothing_saved)


def test_minimum_required():
    """AR-021: publishing without a minimum version is refused with a required error and nothing is saved."""
    with sync_playwright() as p:
        browser, page = open_browser(p)
        snapshot = current_releases(page)
        total = page_props(page)["history"]["total"]
        try:
            for fields in [{"min_version": ""}]:
                submit_expecting_error(page, publish_button(page), "min_version",
                                       "The min version field is required.",
                                       "android", **fields)
            assert_nothing_saved(page, snapshot, total)
        finally:
            restore_releases(page, snapshot)

        browser.close()
