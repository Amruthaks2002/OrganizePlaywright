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

        #creating quiz

        page.get_by_placeholder("Topic, presenter, description...").fill("Automated")

        with open("session_name.txt", "r") as f:
            session_name = f.read()

        page.get_by_text(session_name).click()

        time.sleep(2)
        page.get_by_role("button", name=" Create Quiz ").first.click()
        time.sleep(2)
        page.locator("textarea.w-full").first.fill("Automated quiz description...")
        page.get_by_placeholder("Enter your question…").fill("Question generated via automation...")
        page.get_by_placeholder("Option A…").fill("Playwright Option A")
        page.get_by_placeholder("Option B…").fill("Playwright Option B")
        page.get_by_placeholder("Option C…").fill("Playwright Option C")
        page.get_by_placeholder("Option D…").fill("Playwright Option D")
        time.sleep(1)
        page.get_by_role("button", name=" Add Question (1/20) ").click()
        page.get_by_placeholder("Enter your question…").nth(1).fill("Question generated via automation...")
        page.get_by_placeholder("Option A…").nth(1).fill("Playwright Option A")
        page.get_by_placeholder("Option B…").nth(1).fill("Playwright Option B")
        page.get_by_placeholder("Option C…").nth(1).fill("Playwright Option C")
        page.get_by_placeholder("Option D…").nth(1).fill("Playwright Option D")
        time.sleep(1)
        import re

        page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        time.sleep(3)
        page.get_by_role("button", name="Save Quiz").first.click()
        wait_for_message(page,"Quiz saved successfully.")
        time.sleep(2)

