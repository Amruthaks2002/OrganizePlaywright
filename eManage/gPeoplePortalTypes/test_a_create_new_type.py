
from playwright.sync_api import sync_playwright
from utils.login_helper import login
import time

def wait_for_message(page,text,timeout=10000):
    msg= page.get_by_text(text)
    msg.wait_for(state="visible",timeout=timeout)
    return msg

def test_create_people_portal_type():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()
        login(page)
        page.get_by_test_id("theme-toggle-button").click()

        page.get_by_test_id("sidebar-parent-manage").click()
        time.sleep(1)
        page.get_by_test_id("sidebar-child-people portal types").click()

        page.get_by_placeholder("Ex: Salary Query").fill("Automation query")
        page.get_by_role("button", name="Create Type").click()
        wait_for_message(page, "People Portal type created successfully.")


