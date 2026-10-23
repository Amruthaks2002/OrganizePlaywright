from playwright.sync_api import sync_playwright
from utils.app_usage_helper import (open_browser, load, page_props, install_rows, expected_status,
                                    APP_USAGE_URL, STATUSES)


def test_status_matches_release():
    """AI-014: each install's status follows its platform's release: latest version -> Up to date, newer ->
    Newer than release, between minimum and latest -> Update available, below minimum -> Below minimum,
    no release -> No release published."""
    with sync_playwright() as p:
        browser, page = open_browser(p)
        load(page, APP_USAGE_URL)
        props = page_props(page)

        for row, data in zip(install_rows(page), props["installs"]["data"]):
            expected = expected_status(data["app_version"], props["releases"].get(data["platform"]))
            assert row["status"] == STATUSES[expected], (row, props["releases"])

        browser.close()
