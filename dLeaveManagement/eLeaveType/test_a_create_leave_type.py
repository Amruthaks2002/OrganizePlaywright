from playwright.sync_api import  sync_playwright
from utils.login_helper import login
import time

def wait_for_message(page,text,timeout=10000):
    msg= page.get_by_text(text)
    msg.wait_for(state="visible",timeout=timeout)
    return msg

def test_create_leave_type():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()
        login(page)
        page.get_by_test_id("theme-toggle-button").click()
        page.get_by_test_id("sidebar-parent-leave management").click()
        page.get_by_role("link", name="Leave Type").click()

        #create a new leave type
        page.get_by_role("button", name=" Add Leave Type ").click()
        page.get_by_text("Name *").locator("..").locator("input").fill("Automation")
        page.get_by_text("Code *").locator("..").locator("input").fill("AL")
        page.get_by_text("Yearly Balance").locator("..").locator("input").fill("10")
        page.get_by_role("button", name="Create").click()
        wait_for_message(page,"Leave type created successfully.")


        time.sleep(2)