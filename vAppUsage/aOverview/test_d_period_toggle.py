from datetime import date, timedelta
from playwright.sync_api import sync_playwright, expect
from utils.app_usage_helper import (open_browser, open_app_usage, selected_periods, pick_period, all_kpis,
                                    reload_props, query_params, DEFAULT_PERIOD)


def test_period_toggle():
    """AU-004: the Daily active users chart defaults to 30 days; 7 / 90 days update the URL, the highlighted
    button and the chart's date range, and leave the summary cards alone."""
    with sync_playwright() as p:
        browser, page = open_browser(p)
        open_app_usage(page)
        assert selected_periods(page) == [DEFAULT_PERIOD]
        cards = all_kpis(page)

        for days in [7, 90, 30]:
            pick_period(page, days)
            assert query_params(page).get("period") == str(days), page.url
            assert selected_periods(page) == [days]
            assert all_kpis(page) == cards

            # the chart's data covers exactly the last N days, ending today
            props = reload_props(page)
            assert selected_periods(page) == [days]
            dates = [date.fromisoformat(point["date"]) for point in props["trend"]]
            assert len(dates) == days, len(dates)
            assert dates[-1] == date.today(), dates[-1]
            assert all(b - a == timedelta(days=1) for a, b in zip(dates, dates[1:]))
            expect(page.locator("canvas").first).to_be_visible()

        browser.close()
