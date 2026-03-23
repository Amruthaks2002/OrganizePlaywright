import time

from playwright.sync_api import sync_playwright
from utils.login_helper import login
from playwright.sync_api import expect

def test_manage_users_filters():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        login(page)
        page.get_by_test_id("sidebar-parent-manage").click()
        page.get_by_test_id("sidebar-child-users").click()
        page.get_by_placeholder("Name, email, emp id, hire year").fill("Admin User")
        row = page.locator("tbody tr:has-text('Admin User')")
        expect(row).to_be_visible()
        print("Admin User is visible")
        page.get_by_role("combobox").first.select_option(label="Active")
        page.locator("#vs1__combobox").click()
        page.locator("#vs1__combobox input.vs__search").fill("admin")
        page.locator("li:has-text('admin')").click()
        page.locator("select").nth(1).select_option(value="On-site")
        page.locator("select").nth(2).select_option(value="Night")

        combo = page.locator("#vs2__combobox")
        combo.click()
        search = combo.locator("input.vs__search")
        search.fill("System")
        page.locator("li:has-text('System Administrator')").click()
        time.sleep(3)
        row = page.locator("tbody tr:has-text('Admin User')")
        expect(row).to_be_visible()
        reset_button = page.get_by_role("button",name= "Reset")
        reset_button.click()
        time.sleep(3)



