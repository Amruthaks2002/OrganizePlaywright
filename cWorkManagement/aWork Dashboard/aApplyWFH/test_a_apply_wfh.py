from playwright.sync_api import Page
from playwright.sync_api import sync_playwright
import time

def login(page:Page):
    page.goto("https://organice.qc.iocod.com")
    page.fill("#email","employee@example.com")
    page.fill("#password","password")
    page.click("[data-testid='sign-in-button']")
    page.wait_for_url("**/dashboard**")
    print("Logged in successfully")

def wait_for_message(page,text,timeout=10000):
    msg= page.get_by_text(text)
    msg.wait_for(state="visible",timeout=timeout)
    return msg

def test_a_apply_wfh():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page= context.new_page()

        login(page)
        page.get_by_test_id("theme-toggle-button").click()

        # --- Navigate to Work Management > Work Dashboard ---
        page.get_by_test_id("sidebar-parent-work management").click()
        page.get_by_test_id("sidebar-child-work-dashboard").click()
        page.wait_for_url("**/work-mode/dashboard**")
        page.get_by_role("button", name="Apply Work Mode").click()
        from datetime import datetime
        today_day = str(datetime.now().day)  # e.g. "26"

        calendar_grid = page.locator("div.grid.grid-cols-7").last  # the day-buttons grid
        calendar_grid.locator(f"button:has(span:text-is('{today_day}'))").first.click()

        page.locator("select").select_option(label="Work From Home")

        page.locator("textarea[placeholder='Briefly describe your reason for Work Mode...']").fill(
            "Automation Testing Purposes")

        time.sleep(4)
