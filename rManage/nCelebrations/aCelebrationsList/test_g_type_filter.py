import re
from playwright.sync_api import sync_playwright, expect
from utils.celebrations_helper import (
    open_browser, goto, wide_list_url, type_filter, expect_celebration_listed, settle,
)


def test_type_filter():
    """CEL-007: the type filter shows the work anniversary under Work Anniversary, not under Birthday."""
    with sync_playwright() as p:
        browser, page = open_browser(p)
        goto(page, wide_list_url())

        for kind, listed in [("work_anniversary", True), ("birthday", False), ("", True)]:
            type_filter(page).select_option(kind)
            expect(page).to_have_url(re.compile(rf"type={kind}(&|$)"))
            settle(page)
            expect_celebration_listed(page, listed)

        browser.close()
