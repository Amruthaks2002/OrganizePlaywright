from playwright.sync_api import Playwright, sync_playwright
from utils.login_helper import login
import time

def wait_for_message(page,text,timeout=10000):
    msg= page.get_by_text(text)
    msg.wait_for(state="visible",timeout=timeout)
    return msg

def test_designation_creation():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()
        login(page)
        page.get_by_test_id("sidebar-parent-manage").click()
        time.sleep(1)
        page.get_by_test_id("sidebar-child-designations").click()
        page.get_by_role("button", name="Add New Designation").click()

        page.locator("input[class='w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-teal-500 focus:border-teal-500']").fill("Automation role")
        page.locator("textarea[class='w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-teal-500 focus:border-teal-500']").fill("Automation role description")
        page.get_by_role("button" , name ="Create").click()
        time.sleep(3)
        wait_for_message(page,"Designation created successfully.")
        print("Designation created successfully.")



