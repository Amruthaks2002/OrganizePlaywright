from playwright.sync_api import sync_playwright
from utils.app_usage_helper import (open_browser, open_app_usage, install_rows, installs_count, filter_installs,
                                    search_installs, pick_period, selected_periods, installs_search,
                                    installs_platform_select, installs_status_select, reload_props, query_params,
                                    PLATFORMS, STATUSES)


def test_combined_filters_from_url():
    """AI-010: period, platform, status and search combine, and a reload restores them from the URL."""
    with sync_playwright() as p:
        browser, page = open_browser(p)
        open_app_usage(page)
        target = install_rows(page)[0]
        platform = next(k for k, v in PLATFORMS.items() if v == target["platform"])
        status = next(k for k, v in STATUSES.items() if v == target["status"])

        pick_period(page, 7)
        filter_installs(page, platform=platform, status=status)
        search_installs(page, target["email"])
        assert query_params(page) == {"period": "7", "platform": platform, "status": status,
                                      "search": target["email"]}, page.url
        rows = install_rows(page)
        assert [r["email"] for r in rows] == [target["email"]] * len(rows) and rows, rows

        reload_props(page)
        assert selected_periods(page) == [7]
        assert installs_platform_select(page).input_value() == platform
        assert installs_status_select(page).input_value() == status
        assert installs_search(page).input_value() == target["email"]
        assert install_rows(page) == rows
        assert installs_count(page) == len(rows)

        # a platform that doesn't match the person empties the list
        other = next(k for k in PLATFORMS if k != platform)
        filter_installs(page, platform=other)
        assert [r for r in install_rows(page) if r["email"] == target["email"] and r["platform"] == target["platform"]] == []

        browser.close()
