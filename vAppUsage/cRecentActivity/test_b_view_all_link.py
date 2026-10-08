from playwright.sync_api import sync_playwright, expect
from utils.app_usage_helper import open_browser, open_app_usage, recent_activity_section, heading, ACTIVITIES_URL


def test_view_all_link():
    """RA-002: View all opens the App Activity page."""
    with sync_playwright() as p:
        browser, page = open_browser(p)
        open_app_usage(page)

        recent_activity_section(page).get_by_role("link", name="View all").click()
        expect(page).to_have_url(ACTIVITIES_URL)
        expect(page).to_have_title("App Activity - organice")
        expect(heading(page, "App Activity")).to_be_visible()

        browser.close()
