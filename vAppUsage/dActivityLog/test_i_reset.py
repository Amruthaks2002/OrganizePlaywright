from playwright.sync_api import sync_playwright
from utils.app_usage_helper import (open_browser, load, activity_rows, activities_footer, activity_user_input,
                                    activity_type_select, activity_platform_select, from_date, to_date, reset_button,
                                    filter_activities, default_date_range, query_params, ACTIVITIES_URL)


def test_reset():
    """AL-009: Reset clears every filter and goes back to the last 30 days."""
    with sync_playwright() as p:
        browser, page = open_browser(p)
        load(page, ACTIVITIES_URL)
        rows = activity_rows(page)
        footer = activities_footer(page)
        start, end = default_date_range()

        filter_activities(page, lambda: activity_user_input(page).fill("zzqx-no-such-user"))
        filter_activities(page, lambda: activity_type_select(page).select_option("session.signed_out"))
        filter_activities(page, lambda: activity_platform_select(page).select_option("ios"))
        filter_activities(page, lambda: from_date(page).fill(end))
        assert activity_rows(page) == []

        filter_activities(page, lambda: reset_button(page).click())
        assert activity_user_input(page).input_value() == ""
        assert activity_type_select(page).input_value() == ""
        assert activity_platform_select(page).input_value() == ""
        assert (from_date(page).input_value(), to_date(page).input_value()) == (start, end)
        params = query_params(page)
        assert not params.get("search") and not params.get("action") and not params.get("platform"), page.url
        assert activity_rows(page) == rows
        assert activities_footer(page) == footer

        browser.close()
