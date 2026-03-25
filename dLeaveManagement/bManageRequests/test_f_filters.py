from playwright.sync_api import Playwright, sync_playwright,expect
from utils.login_helper import login
import time

def wait_for_message(page,text,timeout=10000):
    msg= page.get_by_text(text)
    msg.wait_for(state="visible",timeout=timeout)
    return msg

def test_manage_request_filters():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()
        login(page)
        page.get_by_test_id("theme-toggle-button").click()
        page.get_by_test_id("sidebar-parent-leave management").click()
        page.get_by_role("link", name="Manage Requests").click()
        #search for employee user
        page.locator("input[placeholder='Search employee...']").click()
        page.locator("input[placeholder='Search employee...']").fill("employee")
        page.get_by_role("option", name="Employee User").click()

        #check if the table contains the data of employee user
        from playwright.sync_api import expect
        first_cell = page.locator("table tbody tr").first.locator("td").first
        expect(first_cell).to_have_text("Employee User")
        time.sleep(1)