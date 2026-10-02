import re
from playwright.sync_api import sync_playwright, expect
from utils.celebrations_helper import (
    open_browser, goto, wide_list_url, status_filter, expect_celebration_listed, settle,
)


def test_status_filter():
    """CEL-005: the status filter shows the approved celebration only under All / Approved."""
    with sync_playwright() as p:
        browser, page = open_browser(p)
        goto(page, wide_list_url())

        for status, listed in [("approved", True), ("pending", False), ("rejected", False), ("", True)]:
            status_filter(page).select_option(status)
            expect(page).to_have_url(re.compile(rf"status={status}(&|$)"))
            settle(page)
            expect_celebration_listed(page, listed)

        browser.close()
