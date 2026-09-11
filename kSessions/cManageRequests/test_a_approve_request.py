from playwright.sync_api import sync_playwright, expect
from utils.login_helper import login
import time

def wait_for_message(page,text,timeout=10000):
    msg= page.get_by_text(text)
    msg.wait_for(state="visible",timeout=timeout)
    return msg

def test_approve_request():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()
        login(page)
        page.get_by_test_id("theme-toggle-button").click()

        sessions_btn = page.get_by_test_id("sidebar-parent-sessions")
        expect(sessions_btn).to_be_visible()
        expect(sessions_btn).to_be_enabled()
        sessions_btn.click()

        knowledge_hub = page.get_by_test_id("sidebar-child-all-sessions")
        knowledge_hub.wait_for(state="visible")
        knowledge_hub.scroll_into_view_if_needed()
        knowledge_hub.click()

        page.get_by_placeholder("Topic, presenter, description...").fill("Automated")
        time.sleep(1)

        with open("session_name.txt", "r") as f:
            session_name = f.read().strip()

        session_link = page.get_by_text(session_name, exact=False).first
        session_link.wait_for(state="visible")
        session_link.click()
        page.wait_for_url("**/sessions/**")
        time.sleep(2)

        # approving the session request

        page.get_by_test_id("main-content").get_by_role("button", name="Manage").click()
        page.get_by_text("Review Request").wait_for(state="visible")

        page.get_by_role("button", name="Approve Session").click()
        wait_for_message(page, "Session approved successfully.")
        time.sleep(2)

        browser.close()
