from playwright.sync_api import sync_playwright
from utils.app_releases_helper import (open_browser, open_releases, all_history, filter_history, history_rows,
                                       query_params, PLATFORMS, RELEASES_PER_PAGE)


def test_platform_filter():
    """AR-045: picking Android / iOS in History's filter shows only that platform's releases and puts it in the
    URL."""
    with sync_playwright() as p:
        browser, page = open_browser(p)
        releases = all_history(page)

        for platform, label in PLATFORMS.items():
            open_releases(page)
            filter_history(page, platform)
            assert query_params(page).get("platform") == platform, page.url
            rows = history_rows(page)
            assert {r["platform"] for r in rows} <= {label}, [r["platform"] for r in rows]
            expected = min(RELEASES_PER_PAGE, sum(r["platform"] == platform for r in releases))
            assert len(rows) == expected, (platform, len(rows), expected)

        browser.close()
