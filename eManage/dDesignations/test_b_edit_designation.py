from playwright.sync_api import sync_playwright
from utils.login_helper import login
import time

def wait_for_message(page,text,timeout=10000):
    msg= page.get_by_text(text)
    msg.wait_for(state="visible",timeout=timeout)
    return msg

def test_edit_designation():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()
        login(page)
        page.get_by_test_id("theme-toggle-button").click()
        page.get_by_test_id("sidebar-parent-manage").click()
        page.get_by_test_id("sidebar-child-designations").click()
        page.get_by_placeholder("Search designations...").fill("Automation role")
        row = page.locator("tbody tr").filter(has_text="Automation role")
        row.get_by_role("button", name="Edit").click()
        time.sleep(1)

        page.locator("form input[type='text']").fill("Automation role Edited")
        page.locator(
            "textarea[class='w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-teal-500 focus:border-teal-500']").fill(
            "Automation role description edited")
        page.get_by_role("button", name="Update").click()
        time.sleep(2)
        wait_for_message(page, "Designation updated successfully.")
        print("Designation updated successfully.")