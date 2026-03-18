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

        #editing quiz and going quiz live

        page.get_by_placeholder("Topic, presenter, description...").fill("automated")
        page.get_by_role("heading", name="Automated session topic").first.click()
        page.get_by_role("button", name=" Edit Quiz").click()
        page.locator("select").select_option(label="🟢 Go Live")
        time.sleep(2)