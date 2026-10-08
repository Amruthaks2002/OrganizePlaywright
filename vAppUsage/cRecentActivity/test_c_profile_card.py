import re
from playwright.sync_api import sync_playwright, expect
from utils.app_usage_helper import (open_browser, load, page_props, recent_activity_section, open_profile_card,
                                    BASE_URL, APP_USAGE_URL)


def test_profile_card():
    """RA-003: clicking a photo in Recent activity opens the person's profile card and View full profile."""
    with sync_playwright() as p:
        browser, page = open_browser(p)
        load(page, APP_USAGE_URL)
        user = page_props(page)["recentActivity"][0]["user"]

        avatar = recent_activity_section(page).locator("li").first.get_by_role("button")
        name, view_full = open_profile_card(page, avatar)
        assert name == user["name"]

        view_full.click()
        expect(page).to_have_url(f"{BASE_URL}/users/{user['id']}/profile")
        expect(page).to_have_title(re.compile(re.escape(user["name"])))

        browser.close()
