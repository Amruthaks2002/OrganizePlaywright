import re
from playwright.sync_api import sync_playwright, expect
from utils.celebrations_helper import (
    open_browser, goto, wide_list_url, status_filter, type_filter, from_date, to_date,
    expect_celebration_listed, settle,
)


def test_published_filter():
    """CEL-006: choosing Published keeps the filters in the URL and hides the approved celebration.

    Known bug: right after the filtered request the page reloads a bare
    /celebrations, so the URL loses every filter and the Published filter is
    never applied. This test fails until that's fixed.
    """
    with sync_playwright() as p:
        browser, page = open_browser(p)
        goto(page, wide_list_url())

        status_filter(page).select_option("published")
        settle(page)
        page.wait_for_timeout(1500)

        expect(page, "the Published filter should stay in the URL").to_have_url(
            re.compile(r"status=published.*from_date=2020-01-01|from_date=2020-01-01.*status=published"))
        expect(status_filter(page)).to_have_value("published")
        expect(type_filter(page)).to_have_value("")
        expect(from_date(page)).to_have_value("2020-01-01")
        expect(to_date(page)).to_have_value("2030-12-31")
        expect_celebration_listed(page, False)

        browser.close()
