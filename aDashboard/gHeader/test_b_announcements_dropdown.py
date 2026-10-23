import re

from playwright.sync_api import sync_playwright, expect
from utils.dashboard_helper import open_browser_as


def test_announcements_dropdown():
    """DB-050: the announcements button shows a count badge and opens 'Latest Announcements';
    'View all announcements' opens the full list."""
    with sync_playwright() as p:
        browser, page = open_browser_as(p, "admin")
        button = page.get_by_test_id("announcements-button")
        expect(button).to_have_text(re.compile(r"^\s*\d*\s*$"))
        button.click()

        panel = page.locator("div:visible").filter(has=page.get_by_text("Latest Announcements", exact=True)).filter(
            has=page.get_by_text("View all announcements")).last
        expect(panel).to_be_visible()
        panel.get_by_text("View all announcements").click()
        expect(page).to_have_url(re.compile(r"/announcements"))
        browser.close()
