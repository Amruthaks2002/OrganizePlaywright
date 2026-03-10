from datetime import date
import time

from playwright.sync_api import sync_playwright, expect
from utils.login_helper import login

def test_mail_logs_filter():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()

        login(page)

        page.get_by_test_id("theme-toggle-button").click()

        page.get_by_test_id("sidebar-navlink-mail logs").click()

        today = date.today().strftime("%Y-%m-%d")

        page.fill('input[type="date"]', today)

        dates = page.locator("tbody tr td:nth-child(5)")

        for i in range(dates.count()):
            text = dates.nth(i).inner_text()

            if today not in text:
                print("Date mismatch:", text)

        page.get_by_role("button", name=" Reset ").click()
        time.sleep(2)
help


