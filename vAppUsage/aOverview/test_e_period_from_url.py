from playwright.sync_api import sync_playwright
from utils.app_usage_helper import open_browser, load, page_props, selected_periods, APP_USAGE_URL, DEFAULT_PERIOD


def test_period_from_url():
    """AU-005: ?period= in the URL preselects the chart range; an invalid value falls back to 30 days."""
    with sync_playwright() as p:
        browser, page = open_browser(p)

        for days in [7, 90]:
            load(page, f"{APP_USAGE_URL}?period={days}")
            assert selected_periods(page) == [days]
            assert len(page_props(page)["trend"]) == days

        for bad in ["999", "abc", "-7", ""]:
            response = load(page, f"{APP_USAGE_URL}?period={bad}")
            assert response.status == 200, (bad, response.status)
            assert selected_periods(page) == [DEFAULT_PERIOD], bad
            assert len(page_props(page)["trend"]) == DEFAULT_PERIOD, bad

        browser.close()
