from playwright.sync_api import sync_playwright, expect
from utils.app_usage_helper import (open_browser, load, page_props, main_content, activity_rows,
                                    activity_platform_select, filter_activities, query_params, ACTIVITIES_URL,
                                    PLATFORMS, ACTIVITIES_PER_PAGE, ACTIVITIES_EMPTY)


def test_platform_filter():
    """AL-006: the Platform filter lists only that platform's events."""
    with sync_playwright() as p:
        browser, page = open_browser(p)
        load(page, ACTIVITIES_URL)
        all_rows = activity_rows(page)
        complete = page_props(page)["activities"]["total"] <= ACTIVITIES_PER_PAGE

        for value, label in PLATFORMS.items():
            filter_activities(page, lambda: activity_platform_select(page).select_option(value))
            assert query_params(page).get("platform") == value, page.url
            rows = activity_rows(page)
            assert all(r["platform"] == label for r in rows), (label, rows)
            if complete:
                assert len(rows) == len([r for r in all_rows if r["platform"] == label]), label
            if not rows:
                expect(main_content(page).get_by_text(ACTIVITIES_EMPTY)).to_be_visible()

        browser.close()
