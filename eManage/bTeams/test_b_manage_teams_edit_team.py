from playwright.sync_api import sync_playwright
import time
from utils.login_helper import login

def wait_for_message(page,text,timeout=10000):
    msg= page.get_by_text(text)
    msg.wait_for(state="visible",timeout=timeout)
    return msg

def test_edit_teams():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()
        login(page)
        page.get_by_test_id("sidebar-parent-manage").click()
        page.get_by_test_id("sidebar-child-teams").click()
        row = page.locator("tbody tr:has-text('Automation Team')")
        row.wait_for(state="visible")
        row.locator("button.text-indigo-600").click()
        time.sleep(2)

        page.locator("#edit_name").fill("Automation Team edited")
        page.locator("#edit_team_lead_id").select_option(label="Team Lead User")

        page.get_by_role("button", name="Save Changes").click()
        wait_for_message(page,"Team updated successfully.")
