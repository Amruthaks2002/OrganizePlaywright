import re
import time

from playwright.sync_api import sync_playwright
from utils.login_helper import login

def wait_for_message(page, pattern, timeout=10000):
    msg = page.get_by_text(pattern)
    msg.wait_for(state="visible", timeout=timeout)
    return msg

def test_review_queue_reject():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        login(page)
        page.wait_for_url("**/dashboard**")

        # Create a marketplace request first, so there's at least one pending item to reject
        page.get_by_test_id("sidebar-navlink-marketplace").click()
        time.sleep(2)

        page.get_by_role("link", name="Submit application", exact=True).click()
        page.wait_for_url("**/marketplace/create")
        time.sleep(1)

        unique_suffix = str(int(time.time()))
        name = f"Automation App {unique_suffix}"

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
        print("Application submitted for review successfully.")
        time.sleep(2)

        # Go to the review queue and reject the request we just created
        page.goto("https://organice.qc.iocod.com/marketplace/review")
        time.sleep(2)

        name_el = page.get_by_text(name, exact=True)
        card = name_el.locator("xpath=ancestor::div[.//button[normalize-space()='Reject']][1]")
        card.get_by_role("button", name="Reject").click()
        time.sleep(1)

        page.get_by_placeholder("What needs to change?").fill("Rejected by automated Playwright test.")
        page.get_by_role("button", name="Reject submission").click()

        wait_for_message(page, re.compile("was rejected and the author notified", re.I))
        print("Marketplace request rejected successfully.")
        time.sleep(2)
