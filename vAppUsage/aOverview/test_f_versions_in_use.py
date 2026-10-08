from playwright.sync_api import sync_playwright, expect
from utils.app_usage_helper import (open_browser, load, page_props, versions_section, release_chip_texts,
                                    APP_USAGE_URL, APP_RELEASES_URL, STATUSES)


def test_versions_in_use():
    """AU-006: Versions in use shows each platform's latest / minimum version as published on App Releases,
    a chart, and the five version-status chips."""
    with sync_playwright() as p:
        browser, page = open_browser(p)
        load(page, APP_RELEASES_URL)
        current = page_props(page)["current"]

        load(page, APP_USAGE_URL)
        expected = [f"{label}: latest {current[key]['latest_version']}, min {current[key]['min_version']}"
                    for key, label in [("android", "Android"), ("ios", "iOS")] if current.get(key)]
        assert release_chip_texts(page) == expected, release_chip_texts(page)

        section = versions_section(page)
        expect(section.locator("canvas")).to_be_visible()
        chips = [t.strip() for t in section.get_by_role("button").all_inner_texts()]
        assert chips == list(STATUSES.values()), chips

        browser.close()
