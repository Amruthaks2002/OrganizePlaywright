from playwright.sync_api import sync_playwright
from utils.login_helper import login
import time

def wait_for_message(page,text,timeout=10000):
    msg= page.get_by_text(text)
    msg.wait_for(state="visible",timeout=timeout)
    return msg

def test_edit_designation():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()
        login(page)
        page.get_by_test_id("theme-toggle-button").click()
        page.get_by_test_id("sidebar-parent-manage").click()
        time.sleep(1)
        page.get_by_test_id("sidebar-child-designations").click()
        page.get_by_placeholder("Search designations..."    ).fill("Automation role")
        time.sleep(1)
        row = page.locator("tbody tr").filter(has_text="Automation role")
        row.get_by_role("button", name="Edit").click()
        time.sleep(1)

        popup= page.locator(".modal-surface.relative")
        popup.locator(".relative.inline-flex").click()
        page.get_by_role("button", name="Yes, Continue").click()
        wait_for_message(page,"Designation deactivated successfully.")

        page.get_by_role("button", name= "Delete").click()
        page.get_by_text('Delete "Automation role').wait_for()

        page.locator("div.modal-surface").last.get_by_role("button", name="Delete").click()
        time.sleep(3)
        wait_for_message(page, "Designation deleted successfully.")

