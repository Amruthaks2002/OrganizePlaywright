from playwright.sync_api import Playwright, sync_playwright,expect
from utils.login_helper import login
import time

def wait_for_message(page,text,timeout=10000):
    msg= page.get_by_text(text)
    msg.wait_for(state="visible",timeout=timeout)
    return msg

def test_request_reject():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()
        login(page)
        page.get_by_test_id("theme-toggle-button").click()
        page.get_by_test_id("sidebar-parent-leave management").click()
        page.get_by_role("link", name="Manage Requests").click()
        page.locator("tbody tr").first.get_by_role("button", name="View").click()
        page.get_by_role("button", name="Reject").click()
        page.get_by_placeholder("Please provide a reason for rejection...").fill("Rejected by automation")
        form = page.locator("form")
        form.get_by_role("button", name="Reject").click()
        wait_for_message(page,"Leave request rejected.")
