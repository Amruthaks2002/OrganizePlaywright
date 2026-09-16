from playwright.sync_api import sync_playwright , expect
from utils.login_helper import login
import re
import  time

def test_mail_logs_wfh_submitted():
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

        page.locator("select").first.select_option(label="Work Mode Submitted")
        time.sleep(1)

        page.locator("tbody tr").first.get_by_role("link", name="WFH Request Submitted").click()
        expect(page.get_by_text("New Work From Home Request")).to_be_visible()

        with context.expect_page() as new_page_info:
            page.get_by_role("link", name="View Request").click()
        new_page = new_page_info.value
        new_page.wait_for_load_state()
        expect(new_page).to_have_url(re.compile(r".*/hours"))

        browser.close()
