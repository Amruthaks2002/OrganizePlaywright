import re
from playwright.sync_api import sync_playwright
from utils.onboarding_helper import open_browser, open_analytics, analytics_table


def test_confidence_values():
    """OA-005: every confidence is a percentage between 0 and 100 with two decimals."""
    with sync_playwright() as p:
        browser, page = open_browser(p)
        open_analytics(page)

        values = analytics_table(page, "Manual Review Required").locator("tbody tr td:nth-child(3)").all_inner_texts()
        assert values
        for value in values:
            value = value.strip()
            assert re.fullmatch(r"\d{1,3}\.\d{2}%", value) and 0 <= float(value[:-1]) <= 100, value

        browser.close()
