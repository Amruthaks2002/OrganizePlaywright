import time
from playwright.sync_api import sync_playwright
from utils.login_helper import login

def wait_for_message(page, text, timeout=10000):
    msg = page.get_by_text(text)
    msg.wait_for(state="visible", timeout=timeout)
    return msg

def test_edit_users():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        login(page)
        page.get_by_test_id("sidebar-parent-manage").click()
        page.get_by_test_id("sidebar-child-users").click()
        page.get_by_placeholder("Name, email, emp id, hire year").fill("Auto")
        time.sleep(5)
        first_row = page.locator("tbody tr").first
        first_row.get_by_role("button", name="Edit").click()
        time.sleep(5)
        page.locator("#name").fill("Automation Test User Edited")
        page.locator("#emp_id").fill("auto0101")
        page.locator("#email").fill("editeduser@gmail.com")
        page.locator("#personal_email").fill("editedpersonal@gmail.com")
        page.get_by_role("button", name="Save Changes").click()
        time.sleep(5)
        wait_for_message(page, "Employee details updated successfully.")

