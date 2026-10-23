import re
import time

from playwright.sync_api import sync_playwright
from utils.marketplace_helper import open_browser, delete_apps, app_data, review_card, app_card

def wait_for_message(page, pattern, timeout=10000):
    msg = page.get_by_text(pattern)
    msg.wait_for(state="visible", timeout=timeout)
    return msg

def test_edit_marketplace():
    with sync_playwright() as p:
        browser, page = open_browser(p)
        page.wait_for_url("**/dashboard**")

        unique_suffix = str(int(time.time()))
        name = f"Automation App {unique_suffix}"
        try:
            # Create a marketplace request first, so there's at least one item
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
            print("Application submitted for review successfully.")
            time.sleep(2)
            page.get_by_test_id("sidebar-navlink-marketplace").click()
            time.sleep(2)

            # Approve the request we just created

            page.get_by_role("link", name="Review queue", exact=True).click()
            time.sleep(2)

            review_card(page, name).get_by_role("button", name="Approve").click()

            wait_for_message(page, re.compile("is now live in the marketplace", re.I))
            print("Marketplace request approved successfully.")
            time.sleep(2)

            page.get_by_test_id("sidebar-navlink-marketplace").click()
            time.sleep(2)

            # Search for the approved marketplace request
            search_box = page.get_by_placeholder("Search apps, tools and ideas…")
            search_box.fill(name)
            time.sleep(1.5)

            result = app_card(page, name)
            result_text = result.inner_text()
            assert "Approved" in result_text, f"Expected '{name}' to be approved, got: {result_text}"

            result.click()
            time.sleep(2)

            page.get_by_role("link", name="Edit", exact=True).click()
            time.sleep(1)

            page.locator("#short_description").fill("Edited by automated Playwright test.")
            page.locator("#version").fill("1.0.1")

            page.get_by_role("button", name="Submit for review").click()
            wait_for_message(page, re.compile("updated successfully", re.I))
            data = app_data(page, name)
            assert (data["short_description"], data["version"]) == ("Edited by automated Playwright test.", "1.0.1"), data
            print("Marketplace request updated successfully.")
        finally:
            delete_apps(page, name)

        browser.close()
