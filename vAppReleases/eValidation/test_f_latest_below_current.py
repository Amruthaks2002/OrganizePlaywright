from playwright.sync_api import sync_playwright
from utils.app_releases_helper import (open_browser, page_props, current_releases, restore_releases, publish_button,
                                       submit_expecting_error, assert_nothing_saved, lower)


def test_latest_below_current():
    """AR-025: a latest version lower than the current one is refused and nothing is saved."""
    with sync_playwright() as p:
        browser, page = open_browser(p)
        snapshot = current_releases(page)
        total = page_props(page)["history"]["total"]
        release = snapshot["android"]
        try:
            for fields in [{"latest_version": lower(release["latest_version"])}]:
                message = f"The latest version cannot be lower than the current {release['latest_version']}."
                submit_expecting_error(page, publish_button(page), "latest_version", message, "android", **fields)
            assert_nothing_saved(page, snapshot, total)
        finally:
            restore_releases(page, snapshot)

        browser.close()
