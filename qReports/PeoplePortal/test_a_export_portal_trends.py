from playwright.sync_api import sync_playwright, expect
from utils.login_helper import login
import re
import time

def test_people_portal_date_range_filter():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()
        login(page)
        page.get_by_test_id("theme-toggle-button").click()

        reports_btn = page.get_by_test_id("sidebar-parent-reports")
        expect(reports_btn).to_be_visible()
        expect(reports_btn).to_be_enabled()
        reports_btn.click()

        people_portal = page.get_by_test_id("sidebar-child-people-portal")
        people_portal.scroll_into_view_if_needed()
        people_portal.click()
        page.wait_for_url(re.compile(r".*/admin/people-portal/reports"))
        time.sleep(1)

        total_queries = page.locator("text=TOTAL QUERIES").locator("xpath=following-sibling::*[1]")
        default_total = total_queries.inner_text()

        # Widen the date range and confirm the totals actually update
        page.locator("input[type=date]").nth(0).fill("2026-01-01")
        page.locator("input[type=date]").nth(1).fill("2026-12-31")
        page.get_by_role("button", name="Apply").click()
        time.sleep(2)

        widened_total = total_queries.inner_text()
        assert widened_total != default_total, "Total queries did not change after applying a wider date range."
