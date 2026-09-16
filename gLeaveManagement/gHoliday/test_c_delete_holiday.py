from playwright.sync_api import  sync_playwright
from utils.login_helper import login
import time

def wait_for_message(page,text,timeout=10000):
    msg= page.get_by_text(text)
    msg.wait_for(state="visible",timeout=timeout)
    return msg

def test_edit_holiday():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()
        login(page)
        page.get_by_test_id("theme-toggle-button").click()
        page.get_by_test_id("sidebar-parent-leave management").click()
        page.get_by_role("link", name="Holiday").click()
        row = page.locator("tr", has_text="Automation")
        row.get_by_role("button", name="Delete").click()
        modal = page.locator("text=Delete Holiday").locator("..")
        modal.get_by_role("button", name="Delete").click()
        wait_for_message(page,"Holiday deleted successfully.")
        time.sleep(2)