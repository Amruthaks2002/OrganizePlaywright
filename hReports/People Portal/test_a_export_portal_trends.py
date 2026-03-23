from playwright.sync_api import sync_playwright, expect
from utils.login_helper import login
import time

def wait_for_message(page,text,timeout=10000):
    msg= page.get_by_text(text)
    msg.wait_for(state="visible",timeout=timeout)
    return msg

def test_export_people_portal():
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

        wfh_trends= page.get_by_test_id("sidebar-child-people portal")
        wfh_trends.scroll_into_view_if_needed()
        wfh_trends.click()
        time.sleep(2)

        page.get_by_role("button", name=" Export ").click()
        time.sleep(2)

