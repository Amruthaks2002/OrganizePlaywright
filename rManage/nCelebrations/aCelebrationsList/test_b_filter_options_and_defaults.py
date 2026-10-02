import datetime
from playwright.sync_api import sync_playwright, expect
from utils.celebrations_helper import (
    open_browser, open_celebrations, status_filter, from_date, to_date, type_filter, add_months,
)


def test_filter_options_and_defaults():
    """CEL-002: the filters offer the right options; the date range defaults to today .. today + 3 months."""
    with sync_playwright() as p:
        browser, page = open_browser(p)
        open_celebrations(page)
        today = datetime.date.today()

        expect(status_filter(page).locator("option")).to_have_text(
            ["All", "Pending", "Approved", "Rejected", "Published"])
        expect(type_filter(page).locator("option")).to_have_text(["All", "Birthday", "Work Anniversary"])
        expect(status_filter(page)).to_have_value("")
        expect(type_filter(page)).to_have_value("")
        expect(from_date(page)).to_have_value(today.isoformat())
        expect(to_date(page)).to_have_value(add_months(today, 3).isoformat())

        browser.close()
