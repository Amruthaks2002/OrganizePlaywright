from playwright.sync_api import sync_playwright, expect
from utils.login_helper import login
from datetime import datetime
import time

def wait_for_message(page,text,timeout=10000):
    msg= page.get_by_text(text)
    msg.wait_for(state="visible",timeout=timeout)
    return msg

def test_work_mode_logs_filters():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()
        login(page)
        page.get_by_test_id("theme-toggle-button").click()

        page.get_by_test_id("sidebar-parent-logs").click()
        work_mode_logs_link = page.get_by_test_id("sidebar-child-work-mode-logs")
        work_mode_logs_link.wait_for(state="visible")
        work_mode_logs_link.click()
        page.get_by_text("A complete history of all work mode-related actions.").wait_for(state="visible")
        time.sleep(1)

        # grab a real row from the unfiltered table so the filters below are checked
        # against data that actually exists, instead of assuming a fixed employee/date
        first_row = page.locator("table tbody tr").first
        sample_employee = first_row.locator("td").nth(1).text_content().strip()
        sample_action = first_row.locator("td").nth(3).text_content().strip()
        sample_timestamp = first_row.locator("td").nth(0).text_content().strip()
        sample_date_display = ",".join(sample_timestamp.split(",")[:2]).strip()
        sample_date_value = datetime.strptime(sample_date_display, "%d %b, %Y").strftime("%Y-%m-%d")

        # search for the employee from the sample row
        page.locator("input[placeholder='Search by employee...']").click()
        time.sleep(1)
        page.locator("input[placeholder='Search by employee...']").fill(sample_employee)
        time.sleep(1)
        page.get_by_role("option", name=sample_employee).click()
        # check if the table contains the data of the selected employee
        second_cell = page.locator("table tbody tr").first.locator("td").nth(1)
        expect(second_cell).to_have_text(sample_employee)

        page.get_by_role("button", name="Reset").click()
        time.sleep(1)

        # select the action status from the sample row
        page.locator("input[placeholder='Select action status...']").click()
        time.sleep(1)
        page.locator("input[placeholder='Select action status...']").fill(sample_action)
        time.sleep(1)
        page.get_by_role("option", name=sample_action, exact=True).click()
        # check if the table contains the data related to that action
        fourth_cell = page.locator("table tbody tr").first.locator("td").nth(3)
        expect(fourth_cell).to_have_text(sample_action)

        page.get_by_role("button", name="Reset").click()
        time.sleep(1)

        # select the sample row's date in both from and to date fields
        page.locator("input[type='date']").first.fill(sample_date_value)
        page.locator("input[type='date']").last.fill(sample_date_value)

        # check if the table contains that date
        first_cell = page.locator("table tbody tr").first.locator("td").nth(0)
        expect(first_cell).to_contain_text(sample_date_display)
        time.sleep(2)

        browser.close()
