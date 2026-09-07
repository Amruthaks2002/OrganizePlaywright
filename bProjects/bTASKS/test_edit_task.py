from playwright.sync_api import sync_playwright, expect
import time
from utils.login_helper import login


def test_edit_task():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()
        login(page)
        page.click("[data-testid='sidebar-navlink-projects']")
        search_box = page.get_by_placeholder("Search projects...")
        search_box.fill("Automation")
        search_box.press("Enter")
        time.sleep(3)
        page.locator("button[title='Edit']").first.click()
        time.sleep(2)
        page.fill("#edit_name","Automation Task Name edited")
        page.fill("#edit_description","Automation Task description edited")
        page.locator('//*[@id="app"]/div/div/div[2]/main/div/div/div[4]/div[5]/div/div[2]/div/div/form/div[5]/button[2]').click()
        time.sleep(3)




