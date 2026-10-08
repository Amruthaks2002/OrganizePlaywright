import re
from playwright.sync_api import sync_playwright, expect
from utils.app_usage_helper import open_browser, load, page_props, main_content, open_profile_card, BASE_URL, APP_USAGE_URL


def test_profile_card():
    """AI-013: clicking an install's photo opens the person's profile card; View full profile opens their profile."""
    with sync_playwright() as p:
        browser, page = open_browser(p)
        load(page, APP_USAGE_URL)
        user = page_props(page)["installs"]["data"][0]["user"]

        avatar = main_content(page).locator("table tbody tr").first.get_by_role("button")
        name, view_full = open_profile_card(page, avatar)
        assert name == user["name"]
        expect(page.get_by_role("dialog").filter(has_text=name).last).to_be_visible()

        view_full.click()
        expect(page).to_have_url(f"{BASE_URL}/users/{user['id']}/profile")
        expect(page).to_have_title(re.compile(re.escape(user["name"])))

        browser.close()
