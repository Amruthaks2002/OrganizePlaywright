from playwright.sync_api import  sync_playwright
from utils.login_helper import login
import time

def wait_for_message(page,text,timeout=10000):
    msg= page.get_by_text(text)
    msg.wait_for(state="visible",timeout=timeout)
    return msg

def test_delete_policy_leave_type():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()
        login(page)
        page.get_by_test_id("theme-toggle-button").click()
        page.get_by_test_id("sidebar-parent-leave management").click()
        page.get_by_role("link", name="Leave Type").click()
        page.get_by_text("Policy Leave Types", exact=True).click()
        time.sleep(1)

        #delete the created policy leave type
        row = page.locator("table tbody tr", has_text="xcxzcx").filter(has_text="Probation")
        row.get_by_role("button", name="Edit").click()
        time.sleep(1)
        page.get_by_role("button", name="Delete").click()
        time.sleep(1)
        confirm_dialog = page.get_by_role("heading", name="Delete Type Arrangement").locator("xpath=..")
        confirm_dialog.get_by_role("button", name="Delete", exact=True).click()
        wait_for_message(page,"Policy leave type deleted successfully.")
        time.sleep(2)
