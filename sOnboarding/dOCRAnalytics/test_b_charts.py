from playwright.sync_api import sync_playwright, expect
from utils.onboarding_helper import open_browser, open_analytics, analytics_card


def test_charts():
    """OA-002: the Document Types and Extraction Methods charts are drawn."""
    with sync_playwright() as p:
        browser, page = open_browser(p)
        open_analytics(page)

        for heading in ["Document Types", "Extraction Methods"]:
            chart = analytics_card(page, heading).locator("canvas")
            expect(chart).to_be_visible()
            assert chart.evaluate("c => c.width > 0 && c.height > 0"), f"{heading} chart has no size"

        browser.close()
