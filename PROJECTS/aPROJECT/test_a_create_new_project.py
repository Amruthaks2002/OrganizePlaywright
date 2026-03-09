import time
from playwright.sync_api import sync_playwright
from datetime import date
from utils.login_helper import login

def test_project_new():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()
        login(page)
        time.sleep(2)
        page.click("[data-testid='sidebar-navlink-projects']")
        time.sleep(2)
        page.get_by_role("button",name="Create Project").click()
        time.sleep(2)
        page.fill("#name","Automation Project")
        page.select_option("#project_manager_id",index=1)
        page.get_by_label("core development team").click()
        today = date.today().strftime("%Y-%m-%d")
        page.fill("#end_date",today)
        page.select_option("#priority",value="low")
        page.fill("#description","Automation Project description")
        time.sleep(1)
        create_project_btn = page.locator("//form//button[contains(., 'Create Project')]")
        create_project_btn.click()
        time.sleep(3)
