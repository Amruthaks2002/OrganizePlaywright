import re

from playwright.sync_api import sync_playwright, expect
from utils.dashboard_helper import open_browser_as, section_header, BASE_URL


def test_view_all_link():
    """DB-023: View All in the Upcoming Events header opens the Events page."""
    with sync_playwright() as p:
        browser, page = open_browser_as(p, "admin")
        link = section_header(page, "Upcoming Events").get_by_role("link", name="View All")
        expect(link).to_have_attribute("href", f"{BASE_URL}/events")
        link.click()
        expect(page).to_have_url(re.compile(r"/events$"))
        expect(page).to_have_title(re.compile("^Upcoming Events"))
        browser.close()
