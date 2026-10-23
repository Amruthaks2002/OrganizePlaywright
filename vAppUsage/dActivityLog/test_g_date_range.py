from datetime import date, timedelta
from playwright.sync_api import sync_playwright, expect
from utils.app_usage_helper import (open_browser, load, page_props, main_content, activity_rows, activity_time,
                                    from_date, to_date, filter_activities, query_params, ACTIVITIES_URL,
                                    ACTIVITIES_PER_PAGE, ACTIVITIES_EMPTY)


def test_date_range():
    """AL-007: a one-day range lists exactly that day's events (both ends included); a future range is empty."""
    with sync_playwright() as p:
        browser, page = open_browser(p)
        load(page, ACTIVITIES_URL)
        all_rows = activity_rows(page)
        complete = page_props(page)["activities"]["total"] <= ACTIVITIES_PER_PAGE
        day = activity_time(all_rows[-1]["time"]).date()  # oldest event shown, so the range is a real past day

        filter_activities(page, lambda: from_date(page).fill(day.isoformat()))
        filter_activities(page, lambda: to_date(page).fill(day.isoformat()))
        assert (query_params(page)["start_date"], query_params(page)["end_date"]) == (day.isoformat(),) * 2
        rows = activity_rows(page)
        assert rows and all(activity_time(r["time"]).date() == day for r in rows), rows
        if complete:
            assert len(rows) == len([r for r in all_rows if activity_time(r["time"]).date() == day])

        future = date.today() + timedelta(days=1)
        filter_activities(page, lambda: to_date(page).fill((future + timedelta(days=30)).isoformat()))
        filter_activities(page, lambda: from_date(page).fill(future.isoformat()))
        expect(main_content(page).get_by_text(ACTIVITIES_EMPTY)).to_be_visible()
        assert activity_rows(page) == []

        browser.close()
