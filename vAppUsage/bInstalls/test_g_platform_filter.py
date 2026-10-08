from playwright.sync_api import sync_playwright, expect
from utils.app_usage_helper import (open_browser, open_app_usage, main_content, install_rows, installs_count,
                                    filter_installs, installs_platform_select, query_params, PLATFORMS, INSTALLS_EMPTY)


def test_platform_filter():
    """AI-007: the platform filter lists only that platform's installs and updates the count and the URL."""
    with sync_playwright() as p:
        browser, page = open_browser(p)
        open_app_usage(page)
        total = installs_count(page)
        options = installs_platform_select(page).locator("option").all_inner_texts()
        assert [o.strip() for o in options] == ["All platforms"] + list(PLATFORMS.values()), options

        counts = 0
        for value, label in PLATFORMS.items():
            filter_installs(page, platform=value)
            assert query_params(page).get("platform") == value, page.url
            rows = install_rows(page)
            assert all(r["platform"] == label for r in rows), rows
            assert installs_count(page) == len(rows)
            if not rows:
                expect(main_content(page).get_by_text(INSTALLS_EMPTY)).to_be_visible()
            counts += len(rows)
        assert counts == total, (counts, total)

        browser.close()
