from playwright.sync_api import sync_playwright, expect
from utils.app_usage_helper import (open_browser, load, page_props, main_content, heading, activity_rows,
                                    activity_time, activities_footer, activity_user_input, activity_type_select,
                                    activity_platform_select, from_date, to_date, reset_button, default_date_range,
                                    ACTIVITIES_URL, ACTIVITY_COLUMNS)


def test_page_loads():
    """AL-001: App Activity opens with empty filters, the last 30 days selected, the right columns,
    newest events first and a "Showing x – y of z results" footer."""
    with sync_playwright() as p:
        browser, page = open_browser(p)
        load(page, ACTIVITIES_URL)
        main = main_content(page)
        activities = page_props(page)["activities"]

        expect(page).to_have_title("App Activity - organice")
        expect(heading(page, "App Activity")).to_be_visible()
        expect(main.get_by_text("What people did in the mobile app, newest first.")).to_be_visible()
        for label in ["User", "Activity", "Platform", "From Date", "To Date"]:
            expect(main.locator("label", has_text=label).first).to_be_visible()

        assert activity_user_input(page).input_value() == ""
        assert activity_type_select(page).input_value() == ""
        assert activity_platform_select(page).input_value() == ""
        assert (from_date(page).input_value(), to_date(page).input_value()) == default_date_range()
        expect(reset_button(page)).to_be_visible()

        headers = [h.strip().lower() for h in main.locator("table thead th").all_inner_texts()]
        assert headers == [c.lower() for c in ACTIVITY_COLUMNS], headers

        rows = activity_rows(page)
        assert len(rows) == len(activities["data"])
        times = [activity_time(r["time"]) for r in rows]
        assert times == sorted(times, reverse=True), times
        if activities["total"]:
            assert activities_footer(page) == (1, len(rows), activities["total"])

        browser.close()
