import re

from playwright.sync_api import sync_playwright, expect
from utils.dashboard_helper import open_browser_as, open_attendance, section, BASE_URL


def test_stats_card_link():
    """DB-010: the attendance stats card is a link to the Attendance page."""
    with sync_playwright() as p:
        browser, page = open_browser_as(p, "admin")
        open_attendance(page)
        card = section(page, "Attendance").get_by_role("link").filter(has_text="Total Employees")
        expect(card).to_have_attribute("href", f"{BASE_URL}/attendance")
        card.click()
        expect(page).to_have_url(re.compile(r"/attendance$"))
        expect(page).to_have_title(re.compile("^Attendance"))
        browser.close()
