import time

from playwright.sync_api import sync_playwright, expect
from utils.login_helper import login

def test_mail_logs_filter():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()

        login(page)

        page.get_by_test_id("theme-toggle-button").click()

        page.get_by_test_id("sidebar-navlink-mail logs").click()

        page.locator("select").first.select_option(label="Leave Approved")
        time.sleep(2)
        page.wait_for_load_state("networkidle")
        page.locator("tbody tr").first.wait_for()
        users = page.locator("tbody tr td:nth-child(3) span")
        count = users.count()
        for i in range(count):
            text = users.nth(i).text_content().strip()
            assert text == "Leave Approved", f"Unexpected event found: {text}"

        page.locator("select").first.select_option(label="Leave Submitted")
        time.sleep(2)
        page.wait_for_load_state("networkidle")
        page.locator("tbody tr").first.wait_for()
        users = page.locator("tbody tr td:nth-child(3) span")
        count = users.count()
        for i in range(count):
            text = users.nth(i).text_content().strip()
            assert text == "Leave Submitted", f"Unexpected event found: {text}"

        page.locator("select").first.select_option(label="Leave Rejected")
        time.sleep(2)
        page.wait_for_load_state("networkidle")
        page.locator("tbody tr").first.wait_for()
        users = page.locator("tbody tr td:nth-child(3) span")
        count = users.count()
        for i in range(count):
            text = users.nth(i).text_content().strip()
            assert text == "Leave Rejected", f"Unexpected event found: {text}"

        page.locator("select").first.select_option(label="User Created")
        time.sleep(2)
        page.wait_for_load_state("networkidle")
        page.locator("tbody tr").first.wait_for()
        users = page.locator("tbody tr td:nth-child(3) span")
        count = users.count()
        for i in range(count):
            text = users.nth(i).text_content().strip()
            assert text == "User Created", f"Unexpected event found: {text}"

        page.locator("select").first.select_option(label="WFH Submitted")
        time.sleep(2)
        page.wait_for_load_state("networkidle")
        page.locator("tbody tr").first.wait_for()
        users = page.locator("tbody tr td:nth-child(3) span")
        count = users.count()
        for i in range(count):
            text = users.nth(i).text_content().strip()
            assert text == "WFH Submitted", f"Unexpected event found: {text}"

        page.locator("select").first.select_option(label="WFH Rejected")
        time.sleep(2)
        page.wait_for_load_state("networkidle")
        page.locator("tbody tr").first.wait_for()
        users = page.locator("tbody tr td:nth-child(3) span")
        count = users.count()
        for i in range(count):
            text = users.nth(i).text_content().strip()
            assert text == "WFH Rejected", f"Unexpected event found: {text}"

        page.locator("select").first.select_option(label="WFH Approved")
        time.sleep(2)
        page.wait_for_load_state("networkidle")
        page.locator("tbody tr").first.wait_for()
        users = page.locator("tbody tr td:nth-child(3) span")
        count = users.count()
        for i in range(count):
            text = users.nth(i).text_content().strip()
            assert text == "WFH Approved", f"Unexpected event found: {text}"

        page.locator("select").first.select_option(label="Celebration Wish")
        time.sleep(2)
        page.wait_for_load_state("networkidle")
        page.locator("tbody tr").first.wait_for()
        users = page.locator("tbody tr td:nth-child(3) span")
        count = users.count()
        for i in range(count):
            text = users.nth(i).text_content().strip()
            assert text == "Celebration Wish", f"Unexpected event found: {text}"

        page.locator("select").first.select_option(label="Upcoming Celebration Reminder")
        time.sleep(2)
        page.wait_for_load_state("networkidle")
        page.locator("tbody tr").first.wait_for()
        users = page.locator("tbody tr td:nth-child(3) span")
        count = users.count()
        for i in range(count):
            text = users.nth(i).text_content().strip()
            assert text == "Upcoming Celebration Reminder", f"Unexpected event found: {text}"


        page.get_by_role("button", name = " Reset ").click()
        time.sleep(2)

        page.locator("select").last.select_option(label="Sent")
        time.sleep(2)
        page.wait_for_load_state("networkidle")
        page.locator("tbody tr").first.wait_for()
        users = page.locator("tbody tr td:nth-child(4) span")
        count = users.count()
        for i in range(count):
            text = users.nth(i).text_content().strip()
            assert text == "sent", f"Unexpected event found: {text}"

        page.locator("select").last.select_option(label="Failed")
        time.sleep(2)
        page.wait_for_load_state("networkidle")
        page.locator("tbody tr").first.wait_for()
        users = page.locator("tbody tr td:nth-child(4) span")
        count = users.count()
        for i in range(count):
            text = users.nth(i).text_content().strip()
            assert text == "failed", f"Unexpected event found: {text}"



