from playwright.sync_api import Playwright, sync_playwright
from utils.login_helper import login
import time

def wait_for_message(page,text,timeout=10000):
    msg= page.get_by_text(text)
    msg.wait_for(state="visible",timeout=timeout)
    return msg

def test_query_status_solved():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()
        login(page)
        page.get_by_test_id("theme-toggle-button").click()
        page.get_by_test_id("sidebar-navlink-people portal").click()
        page.get_by_role("button", name="Edit").first.click()
        modal = page.locator("div:has(h3:has-text('Edit Query'))")
        modal.locator("label:has-text('Solved')").click()
        page.get_by_placeholder("Add a response that the employee can see in their panel").fill("Response submitted by admin via automation")
        time.sleep(1)
        page.get_by_role("button", name="Save Changes").click()
        wait_for_message(page,"Query updated successfully.")
        time.sleep(1)