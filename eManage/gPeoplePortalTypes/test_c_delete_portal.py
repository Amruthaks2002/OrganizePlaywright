
from playwright.sync_api import sync_playwright
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
        page.get_by_test_id("sidebar-child-people portal types").click()
        page.on("dialog", lambda dialog: dialog.accept())

        page.get_by_role("button", name="Delete").first.click()
        wait_for_message(page,"People Portal type deleted successfully.")

