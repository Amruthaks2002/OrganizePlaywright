from datetime import date, timedelta
from playwright.sync_api import sync_playwright, expect
from utils.app_usage_helper import (open_browser, load, from_date, to_date, filter_activities,
                                    ACTIVITIES_URL, END_BEFORE_START)


def test_end_before_start():
    """AL-008: a To Date earlier than the From Date shows a validation error and stays on App Activity."""
    with sync_playwright() as p:
        browser, page = open_browser(p)
        load(page, ACTIVITIES_URL)
        today = date.today()

        filter_activities(page, lambda: to_date(page).fill((today - timedelta(days=1)).isoformat()))
        filter_activities(page, lambda: from_date(page).fill(today.isoformat()))
        # the message comes up as an error toast, outside the main content
        expect(page.get_by_text(END_BEFORE_START).first).to_be_visible()
        assert page.url.startswith(ACTIVITIES_URL), page.url

        browser.close()
