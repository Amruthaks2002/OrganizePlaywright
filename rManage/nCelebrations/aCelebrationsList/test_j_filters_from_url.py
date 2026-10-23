from playwright.sync_api import sync_playwright, expect
from utils.celebrations_helper import (
    open_browser, goto, list_url, status_filter, from_date, to_date, type_filter, expect_celebration_listed,
)


def test_filters_from_url():
    """CEL-010: opening a URL with filters fills in all four filters and shows the matching celebrations."""
    with sync_playwright() as p:
        browser, page = open_browser(p)
        goto(page, list_url("approved", "2026-01-01", "2026-12-31", "work_anniversary"))

        expect(status_filter(page)).to_have_value("approved")
        expect(from_date(page)).to_have_value("2026-01-01")
        expect(to_date(page)).to_have_value("2026-12-31")
        expect(type_filter(page)).to_have_value("work_anniversary")
        expect_celebration_listed(page, True)

        browser.close()
