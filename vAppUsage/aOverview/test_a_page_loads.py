from playwright.sync_api import sync_playwright, expect
from utils.app_usage_helper import open_browser, open_app_usage, main_content, heading, is_sidebar_active, APP_USAGE_URL


def test_page_loads():
    """AU-001: the App Usage menu opens the page with its heading, the 30-day explanation and the menu item highlighted."""
    with sync_playwright() as p:
        browser, page = open_browser(p)
        open_app_usage(page)
        main = main_content(page)

        expect(page).to_have_url(APP_USAGE_URL)
        expect(page).to_have_title("App Usage - organice")
        expect(heading(page)).to_be_visible()
        expect(main.get_by_text("Installs are counted once someone signs in to the app. "
                                "An install is in use if it was opened in the last 30 days.")).to_be_visible()
        assert is_sidebar_active(page)
        for section in ["Active today", "Active this week", "Installs in use", "On the latest version",
                        "Daily active users", "Recent activity", "Versions in use", "Platforms"]:
            expect(main.locator("h2", has_text=section).first).to_be_visible()
        expect(main.get_by_role("link", name="App Releases")).to_be_visible()

        browser.close()
