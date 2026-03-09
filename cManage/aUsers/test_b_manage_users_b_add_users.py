from playwright.sync_api import sync_playwright
from utils.login_helper import login


def wait_for_message(page, text, timeout=10000):
    msg = page.get_by_text(text)
    msg.wait_for(state="visible", timeout=timeout)
    return msg


def test_manage_users():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()

        login(page)

        page.get_by_test_id("sidebar-parent-manage").click()
        page.get_by_test_id("sidebar-child-users").click()
        page.get_by_role("button", name="Add User").click()

        # -------- Fixed Values --------
        page.locator("#name").fill("Automation Test User")
        page.locator("#emp_id").fill("auto0101")
        page.locator("#email").fill("testuser@gmail.com")
        page.locator("#personal_email").fill("testuserpersonal@gmail.com")

        # Role
        page.locator("#vs4__combobox").click()
        page.locator("#vs4__combobox input").fill("Employee")
        page.locator("body >> li:has-text('Employee')").click()

        # Designation
        page.locator("#vs5__combobox").click()
        page.locator("#vs5__combobox input").fill("Software")
        page.locator("body >> li:has-text('Software Engineer')").click()

        # Work Mode
        page.locator("#vs6__combobox").click()
        page.locator("#vs6__combobox input").fill("on")
        page.locator("body >> li:has-text('On-site')").click()

        # Shift
        page.locator("#vs7__combobox").click()
        page.locator("#vs7__combobox input").fill("mor")
        page.locator("body >> li:has-text('Morning')").click()

        # Manager
        manager_input = page.get_by_placeholder("Select a Reporting Manager")
        manager_input.click()
        manager_input.fill("HR")
        page.locator("body >> li:has-text('HR Manager')").click()

        # Submit
        page.get_by_role("button", name="Create User").click()

        # Wait for success message
        wait_for_message(page, "Employee added successfully.")

        browser.close()
