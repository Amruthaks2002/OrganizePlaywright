from playwright.sync_api import sync_playwright, expect
from utils.onboarding_helper import open_browser, open_analytics, analytics_card


def test_daily_upload_activity():
    """OA-006: Daily Upload Activity shows a chart, or a message when there were no uploads in the period.

    Known bug: when there are no recent uploads the card is left empty - just the heading, no
    chart and no "no data" message. This test fails until that's fixed.
    """
    with sync_playwright() as p:
        browser, page = open_browser(p)
        open_analytics(page)
        page.wait_for_timeout(1500)

        card = analytics_card(page, "Daily Upload Activity")
        has_chart = card.locator("canvas, svg").count() > 0
        has_message = card.inner_text().strip() != "Daily Upload Activity"
        assert has_chart or has_message, "Daily Upload Activity is blank (no chart, no empty-state message)"

        browser.close()
