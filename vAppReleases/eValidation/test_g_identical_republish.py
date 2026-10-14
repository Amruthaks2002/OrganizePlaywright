from playwright.sync_api import sync_playwright
from utils.app_releases_helper import (open_browser, page_props, current_releases, restore_releases, publish_button,
                                       submit, assert_nothing_saved)


def test_identical_republish():
    """AR-026: publishing the current release again unchanged is refused, so History doesn't get a duplicate row.

    Known bug: it's accepted ("Android release 2.1.1 published."), which adds an identical row and moves the
    Published date to now. This test fails until that's fixed, and each failing run leaves one such row (releases
    can't be deleted). The values never change, and the snapshot is restored anyway."""
    with sync_playwright() as p:
        browser, page = open_browser(p)
        snapshot = current_releases(page)
        total = page_props(page)["history"]["total"]
        try:
            submit(page, publish_button(page))  # the form is already filled with the current Android release
            assert_nothing_saved(page, snapshot, total)
        finally:
            restore_releases(page, snapshot)

        browser.close()
