import time

from playwright.sync_api import sync_playwright, expect
from utils.login_helper import login

def test_today_absentees():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()
        login(page)
        page.locator("text=Attendance").click()
        page.locator("a[href*='attendance']").click()
        time.sleep(1)

