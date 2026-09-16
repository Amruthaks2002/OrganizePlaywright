from playwright.sync_api import  sync_playwright
from utils.login_helper import login
import time

def wait_for_message(page,text,timeout=10000):
    msg= page.get_by_text(text)
    msg.wait_for(state="visible",timeout=timeout)
    return msg

def test_edit_policy_leave_type():
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

        #edit the created policy leave type
        row = page.locator("table tbody tr", has_text="xcxzcx").filter(has_text="Probation")
        row.get_by_role("button", name="Edit").click()
        time.sleep(1)
        form = page.locator("form")
        form.get_by_placeholder("Leave empty for unlimited").fill("20")
        form.get_by_role("button", name="Update").click()
        wait_for_message(page,"Policy leave type updated successfully.")
        time.sleep(2)
