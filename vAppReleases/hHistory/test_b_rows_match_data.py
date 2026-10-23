from datetime import datetime

from playwright.sync_api import sync_playwright
from utils.app_releases_helper import (open_browser, open_releases, page_props, history_rows, visible_row,
                                       expected_row, current_ids)


def test_rows_match_data():
    """AR-043: each History row shows its release's date, badges, platform, versions, messages ('Default' when
    empty), author and buttons, newest first."""
    with sync_playwright() as p:
        browser, page = open_browser(p)
        open_releases(page)
        props = page_props(page)
        data = props["history"]["data"]

        assert [visible_row(r) for r in history_rows(page)] == [expected_row(r, current_ids(props)) for r in data]
        times = [datetime.fromisoformat(r["created_at"]) for r in data]
        assert times == sorted(times, reverse=True), times

        browser.close()
