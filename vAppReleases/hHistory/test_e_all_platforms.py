from playwright.sync_api import sync_playwright
from utils.app_releases_helper import (open_browser, open_releases, page_props, filter_history, history_rows,
                                       query_params, visible_row, expected_row, current_ids, APP_RELEASES_URL)


def test_all_platforms():
    """AR-046: switching the filter back to All platforms drops it from the URL and lists every release again (the
    same first page as the unfiltered History)."""
    with sync_playwright() as p:
        browser, page = open_browser(p)
        open_releases(page)
        props = page_props(page)
        open_releases(page, f"{APP_RELEASES_URL}?platform=ios")

        filter_history(page, "all")
        assert "platform" not in query_params(page), page.url
        assert [visible_row(r) for r in history_rows(page)] == \
            [expected_row(r, current_ids(props)) for r in props["history"]["data"]]

        browser.close()
