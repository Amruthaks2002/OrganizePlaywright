from playwright.sync_api import Playwright, sync_playwright,expect
from utils.login_helper import login
import time

def wait_for_message(page,text,timeout=10000):
    msg= page.get_by_text(text)
    msg.wait_for(state="visible",timeout=timeout)
    return msg

def test_query_status_in_progress():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()
        login(page)
        page.get_by_test_id("theme-toggle-button").click()
        page.get_by_test_id("sidebar-parent-leave management").click()
        page.get_by_test_id("sidebar-child-leave dashboard").click()
        page.get_by_role("button", name=" Apply Leave ").click()
        page.get_by_label("Apply leave for multiple employees").check()
        page.get_by_role("button", name="Select All").click()
        time.sleep(2)

        from datetime import datetime
        today = datetime.today().day
        page.locator("button:has(span:text-is('{}'))".format(today)).click()
        page.locator("select").select_option(label="Sick Leave")
        page.get_by_placeholder("Please provide details about your leave request...").fill("Feeling unwell")
        page.get_by_role("button", name="Get AI Suggestions").click()
        page.locator("div.max-h-60 button").first.click()
        page.get_by_role("button", name="Submit Request").click()

        time.sleep(10)
