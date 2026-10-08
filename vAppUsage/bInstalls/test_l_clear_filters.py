from playwright.sync_api import sync_playwright
from utils.app_usage_helper import (open_browser, open_app_usage, install_rows, installs_count, search_installs,
                                    filter_installs, query_params)


def test_clear_filters():
    """AI-012: clearing the search, or going back to All platforms / Any version, brings back every install."""
    with sync_playwright() as p:
        browser, page = open_browser(p)
        open_app_usage(page)
        total = installs_count(page)
        rows = install_rows(page)

        search_installs(page, "zzqx-no-such-install")
        assert installs_count(page) == 0
        search_installs(page, "")
        assert "search" not in query_params(page)
        assert installs_count(page) == total and install_rows(page) == rows

        filter_installs(page, platform="ios", status="unsupported")
        filter_installs(page, platform="", status="")
        assert "platform" not in query_params(page) and "status" not in query_params(page), page.url
        assert installs_count(page) == total and install_rows(page) == rows

        browser.close()
