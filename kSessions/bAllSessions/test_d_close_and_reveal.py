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

        knowledge_hub = page.get_by_test_id("sidebar-child-all sessions")
        knowledge_hub.scroll_into_view_if_needed()
        knowledge_hub.click()



        page.get_by_placeholder("Topic, presenter, description...").fill("Automated")

        with open("session_name.txt", "r") as f:
            session_name = f.read()

        page.get_by_text(session_name).click()
        time.sleep(3)

        # closing and revealing

        page.on("dialog", lambda dialog: dialog.accept())
        page.get_by_role("button", name="Close & Reveal").click()
        wait_for_message(page,"Quiz closed. Results are now visible to all participants.")
        time.sleep(1)