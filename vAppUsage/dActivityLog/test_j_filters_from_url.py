from urllib.parse import urlencode
from playwright.sync_api import sync_playwright
from utils.app_usage_helper import (open_browser, load, reload_props, activity_rows, activity_time, activity_user_input,
                                    activity_type_select, activity_platform_select, from_date, to_date,
                                    ACTIVITIES_URL, ACTIVITY_TYPES, PLATFORMS)


def test_filters_from_url():
    """AL-010: filters in the URL are applied on load and fill in the filter controls, and survive a reload."""
    with sync_playwright() as p:
        browser, page = open_browser(p)
        load(page, ACTIVITIES_URL)
        target = activity_rows(page)[0]
        action = next(k for k, v in ACTIVITY_TYPES.items() if v == target["activity"])
        platform = next(k for k, v in PLATFORMS.items() if v == target["platform"])
        day = activity_time(target["time"]).date().isoformat()

        load(page, f"{ACTIVITIES_URL}?" + urlencode({"search": target["email"], "action": action, "platform": platform,
                                                     "start_date": day, "end_date": day}))
        for _ in range(2):  # straight after loading the link, then after a reload
            assert activity_user_input(page).input_value() == target["email"]
            assert activity_type_select(page).input_value() == action
            assert activity_platform_select(page).input_value() == platform
            assert (from_date(page).input_value(), to_date(page).input_value()) == (day, day)
            rows = activity_rows(page)
            assert target in rows, rows
            for r in rows:
                assert (r["email"], r["activity"], r["platform"]) == (target["email"], target["activity"], target["platform"])
                assert activity_time(r["time"]).date().isoformat() == day
            reload_props(page)

        browser.close()
