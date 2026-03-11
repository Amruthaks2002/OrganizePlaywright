from playwright.sync_api import sync_playwright, expect
from utils.login_helper import login
import time

def wait_for_message(page,text,timeout=10000):
    msg = page.get_by_text(text)
    msg.wait_for(state="visible" , timeout=timeout)
    return msg

def test_delete_feedback():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()
        login(page)
        page.get_by_test_id("sidebar-navlink-feedback & ideas").click()
        view_details_btn = page.locator("//button[text()=' View Details ']")
        view_details_btn.first.click()
        modal = page.locator("div.relative.z-10.transform")
        modal.get_by_role("button" , name ="Mark as Inactive").click()
        time.sleep(1)
        modal.locator("svg.w-5.h-5.text-white").click()
        time.sleep(1)

        view_details_btn = page.locator("//button[text()=' View Details ']")
        view_details_btn.first.click()
        modal.get_by_role("button" , name ="Mark as Active").click()
        time.sleep(1)
        modal.locator("svg.w-5.h-5.text-white").click()


