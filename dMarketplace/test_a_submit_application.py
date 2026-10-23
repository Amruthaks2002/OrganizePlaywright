import re
import time

from playwright.sync_api import sync_playwright
from utils.marketplace_helper import open_browser, delete_apps, app_data

def wait_for_message(page, pattern, timeout=10000):
    msg = page.get_by_text(pattern)
    msg.wait_for(state="visible", timeout=timeout)
    return msg

def test_submit_application():
    with sync_playwright() as p:
        browser, page = open_browser(p)
        page.wait_for_url("**/dashboard**")

        unique_suffix = str(int(time.time()))
        name = f"Automation App {unique_suffix}"
        try:
            page.get_by_test_id("sidebar-navlink-marketplace").click()
            time.sleep(2)

            page.get_by_role("link", name="Submit application", exact=True).click()
            page.wait_for_url("**/marketplace/create")
            time.sleep(1)

            page.locator("#name").fill(name)
            page.locator("#short_description").fill("Automated test submission - short desc.")
            page.locator(".html-editor-content").click()
            page.keyboard.type("This application was submitted by an automated Playwright test.")

            page.locator("#category").select_option("Productivity")
            page.locator("#tags").fill("automation, testing, playwright")
            page.locator("#external_url").fill(f"https://example.com/automation-app-{unique_suffix}")
            page.locator("#version").fill("1.0.0")

            page.get_by_role("button", name="Submit for review").click()
            wait_for_message(page, re.compile("submitted for review", re.I))
            assert app_data(page, name)["status"] == "submitted"
            print("Application submitted for review successfully.")
        finally:
            # remove the submission so it doesn't pile up in the review queue
            delete_apps(page, name)

        browser.close()
