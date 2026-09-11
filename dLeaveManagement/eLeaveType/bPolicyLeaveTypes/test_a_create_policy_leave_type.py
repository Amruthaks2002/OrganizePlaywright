from playwright.sync_api import  sync_playwright
from utils.login_helper import login
import time

def wait_for_message(page,text,timeout=10000):
    msg= page.get_by_text(text)
    msg.wait_for(state="visible",timeout=timeout)
    return msg

def test_create_policy_leave_type():
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

        #create a new policy leave type
        page.get_by_role("button", name="Add Policy Leave Type").click()
        time.sleep(1)
        form = page.locator("form")
        selects = form.locator("select")
        selects.nth(0).select_option(label="xcxzcx (cxcxc)")
        time.sleep(1)
        selects.nth(1).select_option(label="Probation")
        form.get_by_placeholder("Leave empty for unlimited").fill("15")

        form.get_by_role("button", name="Create").click()
        wait_for_message(page,"Policy leave type created successfully.")

        time.sleep(2)
