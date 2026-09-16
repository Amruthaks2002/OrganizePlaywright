import time

from playwright.sync_api import sync_playwright , expect
from utils.login_helper import login

def test_mail_logs_celebration_reminder():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page  = context.new_page()
        login(page)
        page.get_by_test_id("theme-toggle-button").click()

        page.get_by_test_id("sidebar-parent-logs").click()
        mail_log_link = page.get_by_test_id("sidebar-child-mail-log")
        mail_log_link.wait_for(state="visible")
        mail_log_link.click()
        page.get_by_role("heading", name="Mail Logs").wait_for(state="visible")
        time.sleep(1)

        # widen the date range in case this event has no logs in the default window
        page.locator("input[type='date']").first.fill("2020-01-01")
        time.sleep(1)

        page.locator("select").first.select_option(label="Upcoming Celebration Reminder")
        time.sleep(1)

        # subject line varies by which celebrations are upcoming, so click
        # whichever subject link the first row has
        page.locator("tbody tr").first.locator("td").nth(1).get_by_role("link").click()
        time.sleep(1)
        expect(page.get_by_text("Recipient")).to_be_visible()

        browser.close()
