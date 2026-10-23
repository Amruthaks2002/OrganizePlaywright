from playwright.sync_api import sync_playwright, expect
from utils.app_usage_helper import (open_browser, load, main_content, activity_rows, activity_user_input,
                                    filter_activities, ACTIVITIES_URL, ACTIVITIES_EMPTY)


def test_no_match_empty_state():
    """AL-011: a filter that matches nothing shows "No app activity matches these filters." and no rows."""
    with sync_playwright() as p:
        browser, page = open_browser(p)
        load(page, ACTIVITIES_URL)

        filter_activities(page, lambda: activity_user_input(page).fill("zzqx-no-such-user"))
        expect(main_content(page).get_by_text(ACTIVITIES_EMPTY)).to_be_visible()
        assert activity_rows(page) == []

        browser.close()
