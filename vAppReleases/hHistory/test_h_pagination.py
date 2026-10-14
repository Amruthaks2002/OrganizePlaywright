import pytest
from playwright.sync_api import sync_playwright
from utils.app_releases_helper import (open_browser, open_releases, page_props, history_rows, page_link,
                                       wait_for_visit, query_params, visible_row, expected_row, current_ids,
                                       APP_RELEASES_URL, RELEASES_PER_PAGE)


def test_pagination():
    """AR-049: History shows 20 releases a page; the page 2 link shows the following releases and page 1 goes
    back.
    Needs more than 20 releases in History."""
    with sync_playwright() as p:
        browser, page = open_browser(p)
        open_releases(page)
        props = page_props(page)
        history = props["history"]
        assert history["per_page"] == RELEASES_PER_PAGE
        assert len(history_rows(page)) == min(RELEASES_PER_PAGE, history["total"])
        if history["last_page"] < 2:
            browser.close()
            pytest.skip(f"only {history['total']} releases, so History has one page")
        open_releases(page, f"{APP_RELEASES_URL}?page=2")
        page_two = page_props(page)["history"]["data"]
        open_releases(page)

        wait_for_visit(page, lambda: page_link(page, 2).click(), APP_RELEASES_URL)
        assert query_params(page).get("page") == "2", page.url
        assert [visible_row(r) for r in history_rows(page)] == [expected_row(r, current_ids(props)) for r in page_two]

        wait_for_visit(page, lambda: page_link(page, 1).click(), APP_RELEASES_URL)
        assert query_params(page).get("page") in (None, "1"), page.url
        assert len(history_rows(page)) == RELEASES_PER_PAGE

        browser.close()
