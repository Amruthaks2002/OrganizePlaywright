from playwright.sync_api import  sync_playwright
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
        page.get_by_role("link", name=" Leave Audit Logs").click()

        # search for employee user
        page.locator("input[placeholder='Search by employee...']").click()
        time.sleep(1)
        page.locator("input[placeholder='Search by employee...']").fill("employee")
        page.get_by_role("option", name="Employee User").click()
        # check if the table contains the data of employee user
        from playwright.sync_api import expect
        second_cell = page.locator("table tbody tr").first.locator("td").nth(1)
        expect(second_cell).to_have_text("Employee User")

        #select the action status "created"
        page.locator("input[placeholder='Select action status...']").click()
        page.locator("input[placeholder='Select action status...']").fill("create")
        page.get_by_role("option", name="Created").click()
        # check if the table contains the data related to created
        fourth_cell = page.locator("table tbody tr").first.locator("td").nth(3)
        expect(fourth_cell).to_have_text("Created")

        #select today's date in both from and to date fields
        from datetime import datetime
        today = datetime.today().strftime("%Y-%m-%d")
        page.locator("input[type='date']").first.fill(today)

        today = datetime.today().strftime("%Y-%m-%d")
        page.locator("input[type='date']").last.fill(today)
        #check if the table contains today's date
        first_cell = page.locator("table tbody tr").first.locator("td").nth(0)
        expect(first_cell).to_contain_text("23 Mar 2026")
        time.sleep(2)

