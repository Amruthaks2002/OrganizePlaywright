from playwright.sync_api import sync_playwright, expect
from utils.login_helper import login
import time
from datetime import datetime


def test_filters_idea():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()
        login(page)

        page.get_by_test_id("sidebar-navlink-feedback & ideas").click()
        import re

        expect(page).to_have_url(re.compile(r".*/admin/feedback-submissions.*"))

        page.click("div.feedback-user-select")
        search_input = page.locator("input.vs__search")
        search_input.fill("Admin")
        page.locator("li:has-text('Admin User')").click()
        time.sleep(1)

        today=datetime.today().strftime("%Y-%m-%d")
        date_input = page.locator("input[type='date']").first
        date_input.fill(today)

        to_date_input = page.locator("input[type='date']").last
        to_date_input.fill(today)
        time.sleep(1)

        page.get_by_role("button", name = "Reset Filters").click()
        time.sleep(2)

        page.get_by_role("button", name="Today").click()
        time.sleep(1)
        expect(page).to_have_url(re.compile(r".*?date_filter=today.*"))
        page.get_by_role("button", name="This Week").click()
        expect(page).to_have_url(re.compile(r".*?date_filter=week.*"))
        time.sleep(1)
        page.get_by_role("button", name="This Month").click()
        expect(page).to_have_url(re.compile(r".*?date_filter=month.*"))
        time.sleep(1)




