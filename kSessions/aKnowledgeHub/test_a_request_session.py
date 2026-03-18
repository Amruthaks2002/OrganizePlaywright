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

        knowledge_hub = page.get_by_test_id("sidebar-child-knowledge hub")
        knowledge_hub.scroll_into_view_if_needed()
        knowledge_hub.click()

        page.get_by_role("button" , name=" Request Session ").click()
        page.locator("#sessionTopic").fill("Automated session topic")
        page.locator("#description").fill("Automated session description")

        from datetime import datetime
        today = datetime.today().strftime("%Y-%m-%d")
        page.locator("#preferredDate").fill(today)

        page.get_by_role("button" , name=" Submit Request ").click()
        wait_for_message(page,"Session request submitted successfully.")
        time.sleep(2)

        #go to all sessions by clicking on view archive
        page.get_by_role("link" , name="View Archive").click()
        time.sleep(2)
        expect(page).to_have_url("https://organice.qc.iocod.com/sessions/all")