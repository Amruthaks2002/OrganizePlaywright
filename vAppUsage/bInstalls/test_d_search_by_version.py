from playwright.sync_api import sync_playwright
from utils.app_usage_helper import open_browser, open_app_usage, install_rows, installs_count, search_installs


def test_search_by_version():
    """AI-004: searching an app version lists the installs on that version."""
    with sync_playwright() as p:
        browser, page = open_browser(p)
        open_app_usage(page)
        all_rows = install_rows(page)
        version = all_rows[0]["version"].split("+")[0]

        search_installs(page, version)
        rows = install_rows(page)
        expected = [r["email"] for r in all_rows if r["version"].split("+")[0] == version]
        assert sorted(r["email"] for r in rows) == sorted(expected), rows
        assert installs_count(page) == len(rows)

        browser.close()
