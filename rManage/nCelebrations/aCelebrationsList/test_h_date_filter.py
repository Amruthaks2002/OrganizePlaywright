from playwright.sync_api import sync_playwright
from utils.celebrations_helper import (
    open_browser, goto, wide_list_url, from_date, to_date, set_filter_date, expect_celebration_listed,
)


def test_date_filter():
    """CEL-008: the date range hides the celebration when it excludes June 4 2026 and shows it when it includes it."""
    with sync_playwright() as p:
        browser, page = open_browser(p)
        goto(page, wide_list_url())

        set_filter_date(page, from_date(page), "2026-06-05")
        expect_celebration_listed(page, False)

        set_filter_date(page, from_date(page), "2026-06-04")
        set_filter_date(page, to_date(page), "2026-06-04")
        expect_celebration_listed(page, True)

        set_filter_date(page, to_date(page), "2026-06-03")
        expect_celebration_listed(page, False)

        set_filter_date(page, from_date(page), "2026-05-01")
        set_filter_date(page, to_date(page), "2026-06-30")
        expect_celebration_listed(page, True)

        browser.close()
