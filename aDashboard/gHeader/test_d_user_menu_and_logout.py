import re

from playwright.sync_api import sync_playwright, expect
from utils.dashboard_helper import open_browser_as, ADMIN, BASE_URL, DASHBOARD_URL


def test_user_menu_and_logout():
    """DB-052: the user menu shows the user's name and designation and links to Profile and
    Notifications; Log Out signs out, after which the dashboard redirects to the login page."""
    with sync_playwright() as p:
        browser, page = open_browser_as(p, "admin")
        expect(page.get_by_test_id("user-name")).to_have_text(ADMIN["name"])
        expect(page.get_by_test_id("user-designation")).to_have_text(ADMIN["designation"])

        page.get_by_test_id("user-profile-button").click()
        menu = page.get_by_test_id("dropdown-content")
        expect(menu).to_be_visible()
        links = menu.get_by_test_id("profile-link")
        expect(links).to_have_count(2)
        expect(links.filter(has_text="Profile")).to_have_attribute("href", f"{BASE_URL}/profile")
        expect(links.filter(has_text="Notifications")).to_have_attribute("href", f"{BASE_URL}/notifications")

        page.get_by_test_id("user-logout-link").click()
        expect(page).to_have_url(re.compile(rf"^{BASE_URL}/(login)?$"))
        page.goto(DASHBOARD_URL)
        expect(page).to_have_url(re.compile(r"/login$"))
        browser.close()
