from playwright.sync_api import sync_playwright, expect
from utils.login_helper import login
import time

def wait_for_message(page,text,timeout=10000):
    msg= page.get_by_text(text)
    msg.wait_for(state="visible",timeout=timeout)
    return msg

def test_bank_document():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()
        login(page)
        page.get_by_test_id("theme-toggle-button").click()

        from playwright.sync_api import expect

        sessions_btn = page.get_by_test_id("sidebar-parent-sessions")
        expect(sessions_btn).to_be_visible()
        expect(sessions_btn).to_be_enabled()
        sessions_btn.click()
        time.sleep(2)

        page.get_by_role("link", name="Manage Requests").click()

        #page.get_by_role("button", name="Manage").click()
        #page.locator("//button[.//span[text()='Manage']]").click()
        #page.get_by_text("Manage").click()
        #page.locator("span:has-text('Manage')").click()
        #page.locator("//button[contains(.,'Manage')]").click()
        #page.locator("button.group\\/btn").click()
        #page.locator("button:has-text('Manage')").click()



        time.sleep(10)
