from playwright.sync_api import sync_playwright, expect
from utils.login_helper import login
import time

def wait_for_message(page,text,timeout=10000):
    msg= page.get_by_text(text)
    msg.wait_for(state="visible",timeout=timeout)
    return msg

def test_quiz_go_live():
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

        #editing quiz and going quiz live

        page.get_by_placeholder("Topic, presenter, description...").fill("Automated")
        time.sleep(1)

        with open("session_name.txt", "r") as f:
            session_name = f.read().strip()

        session_link = page.get_by_text(session_name, exact=False).first
        session_link.wait_for(state="visible")
        session_link.click()
        page.wait_for_url("**/sessions/**")
        time.sleep(2)

        page.get_by_role("button", name=" Edit Quiz").click()
        time.sleep(1)

        status_dropdown = page.get_by_role("combobox").first
        status_dropdown.click()
        status_dropdown.select_option("🟢 Go Live")
        time.sleep(1)

        browser.close()