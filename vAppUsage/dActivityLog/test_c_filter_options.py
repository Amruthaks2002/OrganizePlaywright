from playwright.sync_api import sync_playwright
from utils.app_usage_helper import (open_browser, load, activity_type_select, activity_platform_select,
                                    ACTIVITIES_URL, ACTIVITY_TYPES, PLATFORMS)


def options(select):
    return select.locator("option").evaluate_all("os => os.map(o => [o.value, o.textContent.trim()])")


def test_filter_options():
    """AL-003: the Activity filter lists all 25 kinds of app activity; the Platform filter lists Android and iOS."""
    with sync_playwright() as p:
        browser, page = open_browser(p)
        load(page, ACTIVITIES_URL)

        assert options(activity_type_select(page)) == [["", "All activities"]] + [list(t) for t in ACTIVITY_TYPES.items()]
        assert options(activity_platform_select(page)) == [["", "All platforms"]] + [list(t) for t in PLATFORMS.items()]

        browser.close()
