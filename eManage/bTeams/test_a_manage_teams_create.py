from playwright.sync_api import sync_playwright
import time
from utils.login_helper import login

def wait_for_message(page,text,timeout=10000):
    msg= page.get_by_text(text)
    msg.wait_for(state="visible",timeout=timeout)
    return msg

def test_team_creation():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()
        login(page)
        page.get_by_test_id("sidebar-parent-manage").click()
        page.get_by_test_id("sidebar-child-teams").click()
        page.get_by_role("button", name="Create Team").click()
        team_lead_input = page.get_by_placeholder("Select a Team Lead")
        team_lead_input.click()
        page.locator("body >> li[role='option']").first.click()
        page.locator("#name").fill("Automation Team")
        page.locator("button[type='submit']").click()
        time.sleep(4)
        wait_for_message(page,"Team created successfully with 1 member(s).")
        print("success message has appeared")








