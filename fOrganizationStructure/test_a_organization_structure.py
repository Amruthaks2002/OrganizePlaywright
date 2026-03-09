from playwright.sync_api import sync_playwright, expect
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
        page.get_by_test_id("sidebar-navlink-organization structure").click()
        time.sleep(2)
        page.get_by_test_id("enter-fullscreen-button").click()
        time.sleep(3)
        page.get_by_test_id("exit-fullscreen-button").click()
        time.sleep(2)
        page.get_by_role("button", name="Collapse").click()
        time.sleep(2)
        page.get_by_role("button", name="Expand").click()
        time.sleep(2)
        page.get_by_placeholder("Search employees...").fill("admin")
        time.sleep(2)
        page.locator(".boc-node--card").first.click()
        time.sleep(2)
        page.get_by_test_id("performance-modal-report-link").click()
        import re
        expect(page).to_have_url(re.compile(r".*/performance*"))
        time.sleep(2)
        page.get_by_role("link", name=" View Full Year Leave Details → ").click()
        expect(page).to_have_url(re.compile(r".*/year-end-records*"))
