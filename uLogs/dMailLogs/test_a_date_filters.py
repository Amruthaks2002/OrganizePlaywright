from datetime import date
import time

from playwright.sync_api import sync_playwright, expect
from utils.login_helper import login

def test_mail_logs_date_filter():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()

        login(page)

        page.get_by_test_id("theme-toggle-button").click()

        page.get_by_test_id("sidebar-parent-logs").click()
        mail_log_link = page.get_by_test_id("sidebar-child-mail-log")
        mail_log_link.wait_for(state="visible")
        mail_log_link.click()
        page.get_by_role("heading", name="Mail Logs").wait_for(state="visible")
        time.sleep(1)

        today = date.today().strftime("%Y-%m-%d")

        page.locator("input[type='date']").first.fill(today)
        page.locator("input[type='date']").last.fill(today)
        time.sleep(1)

        today_display = date.today().strftime("%-d %b, %Y")
        dates = page.locator("tbody tr td:nth-child(5)")
        row_count = dates.count()
        assert row_count > 0
        for i in range(row_count):
            expect(dates.nth(i)).to_contain_text(today_display)

        page.get_by_role("button", name="Reset").click()
        time.sleep(2)

        browser.close()
