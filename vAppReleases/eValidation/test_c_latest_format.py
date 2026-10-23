from playwright.sync_api import sync_playwright
from utils.app_releases_helper import (open_browser, page_props, current_releases, restore_releases, publish_button,
                                       submit_expecting_error, assert_nothing_saved, VERSION_FORMAT)


def test_latest_format():
    """AR-022: a latest version that isn't numbers and dots is refused ('Use a version like 1.4.0.') and nothing
    is saved."""
    with sync_playwright() as p:
        browser, page = open_browser(p)
        snapshot = current_releases(page)
        total = page_props(page)["history"]["total"]
        try:
            for fields in [{"latest_version": "abc"}, {"latest_version": "1.a.0"}]:
                submit_expecting_error(page, publish_button(page), "latest_version",
                                       VERSION_FORMAT,
                                       "android", **fields)
            assert_nothing_saved(page, snapshot, total)
        finally:
            restore_releases(page, snapshot)

        browser.close()
