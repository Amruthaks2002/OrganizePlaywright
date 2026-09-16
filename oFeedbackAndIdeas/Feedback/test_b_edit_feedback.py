from playwright.sync_api import sync_playwright
from utils.login_helper import login
import time

def wait_for_message(page,text,timeout=10000):
    msg = page.get_by_text(text)
    msg.wait_for(state="visible", timeout=timeout)
    return msg

def test_b_edit_feedback():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page=context.new_page()
        login(page)
        page.get_by_test_id("sidebar-navlink-feedback & ideas").click()
        view_details_btn = page.locator("//button[text()=' View Details ']")
        view_details_btn.first.click()
        time.sleep(1)
        modal = page.locator("div.relative.z-10.transform")
        modal.get_by_role("button", name ="Edit").click()
        time.sleep(2)
        page.locator("textarea").fill("Automation note edited")
        page.get_by_role("button", name=" Save Changes ").click()
        time.sleep(2)
        wait_for_message(page,"Updated successfully.")


