from playwright.sync_api import sync_playwright
from utils.app_usage_helper import (open_browser, load, page_props, install_rows, installs_count,
                                    installs_platform_select, installs_status_select, APP_USAGE_URL)


def test_invalid_url_filters_ignored():
    """AI-011: unknown platform / status values in the URL are ignored and the full list is shown."""
    with sync_playwright() as p:
        browser, page = open_browser(p)
        load(page, APP_USAGE_URL)
        total = installs_count(page)
        rows = install_rows(page)

        for query in ["?status=bogus", "?platform=windows", "?platform=windows&status=bogus"]:
            response = load(page, APP_USAGE_URL + query)
            assert response.status == 200, (query, response.status)
            assert page.url == APP_USAGE_URL + query
            filters = page_props(page)["filters"]
            assert filters["platform"] is None and filters["status"] is None, (query, filters)
            assert installs_platform_select(page).input_value() == ""
            assert installs_status_select(page).input_value() == ""
            assert installs_count(page) == total
            assert install_rows(page) == rows

        browser.close()
