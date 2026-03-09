from playwright.sync_api import sync_playwright, expect
from utils.login_helper import login
import time
import re


def wait_for_message(page,text,timeout=10000):
    msg= page.get_by_text(text)
    msg.wait_for(state="visible",timeout=timeout)
    return msg

def test_filters():
    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=False,
            args=["--start-maximized"]
        )
        context = browser.new_context(no_viewport=True)
        page = context.new_page()
        login(page)
        page.get_by_test_id("sidebar-navlink-audit logs").click()
        expect(page).to_have_url(re.compile(r".*/audits*"))


        page.locator("select").first.select_option(label="User")
        time.sleep(2)
        page.locator("tbody tr").first.locator("button:has-text('View')").click()
        time.sleep(2)
        expect(page).to_have_url(re.compile(r".*/audits/entity*"))
        expect(page.get_by_text("App\\Models\\User")).to_be_visible()
        page.get_by_role("link", name="Back To Audit Logs").click()
        expect(page).to_have_url(re.compile(r".*/audits*"))


        page.locator("select").first.select_option(label="LeaveApplication")
        time.sleep(2)
        page.locator("tbody tr").first.locator("button:has-text('View')").click()
        time.sleep(5)
        expect(page).to_have_url(re.compile(r".*/audits/entity*"))
        expect(page.get_by_text("App\\Models\\LeaveApplication")).to_be_visible()
        page.get_by_role("link", name="Back To Audit Logs").click()
        expect(page).to_have_url(re.compile(r".*/audits*"))


        page.locator("select").first.select_option(label="Project")
        time.sleep(2)
        page.locator("tbody tr").first.locator("button:has-text('View')").click()
        time.sleep(5)
        expect(page).to_have_url(re.compile(r".*/audits/entity*"))
        expect(page.get_by_text("App\\Models\\Project")).to_be_visible()
        page.get_by_role("link", name="Back To Audit Logs").click()
        expect(page).to_have_url(re.compile(r".*/audits*"))


        page.locator("select").first.select_option(label="LeaveType")
        time.sleep(3)
        page.locator("tbody tr").first.locator("button:has-text('View')").click()
        time.sleep(2)
        expect(page.get_by_text("App\\Models\\LeaveType")).to_be_visible()
        expect(page).to_have_url(re.compile(r".*/audits/entity*"))
        page.get_by_role("link", name="Back To Audit Logs").click()
        expect(page).to_have_url(re.compile(r".*/audits*"))


        page.locator("select").first.select_option(label="PeoplePortalQuery")
        time.sleep(3)
        page.locator("tbody tr").first.locator("button:has-text('View')").click()
        expect(page).to_have_url(re.compile(r".*/audits/entity*"))
        time.sleep(3)
        expect(page.get_by_text("App\\Models\\PeoplePortalQuery")).to_be_visible()
        page.get_by_role("link", name="Back To Audit Logs").click()
        expect(page).to_have_url(re.compile(r".*/audits*"))

