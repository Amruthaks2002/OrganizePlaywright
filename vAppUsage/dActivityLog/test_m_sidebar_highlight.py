from playwright.sync_api import sync_playwright, expect
from utils.app_usage_helper import (open_browser, open_app_usage, recent_activity_section, is_sidebar_active,
                                    ACTIVITIES_URL)


def test_sidebar_highlight():
    """AL-013: App Activity belongs to App Usage, so the App Usage menu item stays highlighted there.

    Known bug: after View all, nothing in the sidebar is highlighted on /manage/app-usage/activities.
    This test fails until that's fixed."""
    with sync_playwright() as p:
        browser, page = open_browser(p)
        open_app_usage(page)
        assert is_sidebar_active(page)

        recent_activity_section(page).get_by_role("link", name="View all").click()
        expect(page).to_have_url(ACTIVITIES_URL)
        assert is_sidebar_active(page), "App Usage is not highlighted in the sidebar on the App Activity page"

        browser.close()
