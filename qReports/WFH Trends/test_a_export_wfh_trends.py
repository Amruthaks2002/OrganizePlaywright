from playwright.sync_api import sync_playwright, expect
from utils.login_helper import login
import re
import time

def wait_for_message(page,text,timeout=10000):
    msg= page.get_by_text(text)
    msg.wait_for(state="visible",timeout=timeout)
    return msg

def test_export_wfh_trends():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()
        login(page)
        page.get_by_test_id("theme-toggle-button").click()

        from playwright.sync_api import expect

        reports_btn = page.get_by_test_id("sidebar-parent-reports")
        expect(reports_btn).to_be_visible()
        expect(reports_btn).to_be_enabled()
        reports_btn.click()

        leave_trends= page.get_by_test_id("sidebar-child-work-mode-trends")
        leave_trends.scroll_into_view_if_needed()
        leave_trends.click()
        page.wait_for_url(re.compile(r".*/reports/work-mode-trends"))
        time.sleep(1)

        page.get_by_role("button", name="Export Excel").click()
        wait_for_message(page, "Work mode summary export has been started.")
        time.sleep(2)

