from playwright.sync_api import sync_playwright, expect
from utils.login_helper import login
from datetime import datetime
import time

def wait_for_message(page,text,timeout=10000):
    msg= page.get_by_text(text)
    msg.wait_for(state="visible",timeout=timeout)
    return msg

def test_leave_audit_logs_filters():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()
        login(page)
        page.get_by_test_id("theme-toggle-button").click()

        page.get_by_test_id("sidebar-parent-logs").click()
        audit_logs_link = page.get_by_test_id("sidebar-child-leave-audit-logs")
        audit_logs_link.wait_for(state="visible")
        audit_logs_link.click()
        page.get_by_text("A complete history of all leave-related actions.").wait_for(state="visible")
        time.sleep(1)

        # search for employee user
        page.locator("input[placeholder='Search by employee...']").click()
        time.sleep(1)
        page.locator("input[placeholder='Search by employee...']").fill("employee")
        time.sleep(1)
        page.get_by_role("option", name="Employee User").click()
        # check if the table contains the data of employee user
        second_cell = page.locator("table tbody tr").first.locator("td").nth(1)
        expect(second_cell).to_have_text("Employee User")

        page.get_by_role("button", name="Reset").click()
        time.sleep(1)

        #select the action status "created"
        page.locator("input[placeholder='Select action status...']").click()
        time.sleep(1)
        page.locator("input[placeholder='Select action status...']").fill("create")
        time.sleep(1)
        page.get_by_role("option", name="Created").click()
        # check if the table contains the data related to created
        fourth_cell = page.locator("table tbody tr").first.locator("td").nth(3)
        expect(fourth_cell).to_have_text("Created")

        page.get_by_role("button", name="Reset").click()
        time.sleep(1)

        #select today's date in both from and to date fields
        today = datetime.today().strftime("%Y-%m-%d")
        page.locator("input[type='date']").first.fill(today)
        page.locator("input[type='date']").last.fill(today)

        #check if the table contains today's date
        today_display = datetime.today().strftime("%-d %b, %Y")
        first_cell = page.locator("table tbody tr").first.locator("td").nth(0)
        expect(first_cell).to_contain_text(today_display)
        time.sleep(2)

        browser.close()

