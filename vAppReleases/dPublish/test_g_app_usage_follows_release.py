from playwright.sync_api import sync_playwright
from utils.app_releases_helper import (open_browser, page_props, current_releases, restore_releases, publish,
                                       expect_toast, load, raised_min, APP_USAGE_URL)
from utils.app_usage_helper import release_chip_texts, expected_status, STATUSES, main_content


def test_app_usage_follows_release():
    """AR-019: after a new minimum is published, App Usage's Versions in use shows it and each install's status is
    worked out against it. The new minimum stays at or below the latest (no install is blocked); the snapshot is
    restored afterwards."""
    with sync_playwright() as p:
        browser, page = open_browser(p)
        snapshot = current_releases(page)
        old = page_props(page)["current"]["android"]
        latest, minimum = old["latest_version"], raised_min(old)
        try:
            publish(page, "android", latest_version=latest, min_version=minimum)
            expect_toast(page, f"Android release {latest} published.")

            load(page, APP_USAGE_URL)
            props = page_props(page)
            assert f"Android: latest {latest}, min {minimum}" in release_chip_texts(page), release_chip_texts(page)
            assert props["releases"]["android"]["min_version"] == minimum, props["releases"]
            # only the status badge is read: installs counted before sign-in have no user in the first cell
            badges = main_content(page).locator("table tbody tr td:nth-child(3) span.rounded-full").all_inner_texts()
            data = props["installs"]["data"]
            assert len(badges) == len(data), (badges, len(data))
            for badge, install in zip(badges, data):
                expected = expected_status(install["app_version"], props["releases"].get(install["platform"]))
                assert badge.strip() == STATUSES[expected], (install, props["releases"])
        finally:
            restore_releases(page, snapshot)

        browser.close()
