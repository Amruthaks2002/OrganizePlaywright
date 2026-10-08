from playwright.sync_api import sync_playwright
from utils.app_usage_helper import (open_browser, open_app_usage, install_rows, installs_count, status_chip,
                                    is_chip_active, installs_status_select, wait_for_visit, query_params, STATUSES)


def test_status_chips():
    """AI-009: clicking a status chip under Versions in use filters the installs, sets the dropdown and highlights
    the chip; clicking it again clears the filter."""
    with sync_playwright() as p:
        browser, page = open_browser(p)
        open_app_usage(page)
        total = installs_count(page)

        for value, label in STATUSES.items():
            wait_for_visit(page, lambda: status_chip(page, value).click())
            assert query_params(page).get("status") == value, page.url
            assert installs_status_select(page).input_value() == value
            assert is_chip_active(page, value)
            assert [s for s in STATUSES if s != value and is_chip_active(page, s)] == []
            assert all(r["status"] == label for r in install_rows(page))

            wait_for_visit(page, lambda: status_chip(page, value).click())
            assert "status" not in query_params(page), page.url
            assert installs_status_select(page).input_value() == ""
            assert not is_chip_active(page, value)
            assert installs_count(page) == total

        browser.close()
