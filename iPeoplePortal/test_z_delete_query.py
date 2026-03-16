from playwright.sync_api import Page
from playwright.sync_api import sync_playwright
import time

def login(page:Page):
    page.goto("https://organice.qc.iocod.com")
    page.fill("#email", "employee@example.com")
    page.fill("#password", "password")
    page.click("[data-testid='sign-in-button']")
    page.wait_for_url("**/dashboard**")
    print("✔ Logged in successfully")


def wait_for_message(page,text,timeout=10000):
    msg= page.get_by_text(text)
    msg.wait_for(state="visible",timeout=timeout)
    return msg

def test_delete_query():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()
        login(page)
        page.get_by_test_id("theme-toggle-button").click()
        page.get_by_test_id("sidebar-navlink-people portal").click()

        page.get_by_role("button", name="+ New Query").click()

        modal = page.locator(".fixed.inset-0.z-50")
        modal.wait_for()
        modal.locator(".vs__dropdown-toggle").click()
        modal.locator("input.vs__search").fill("Other queries")
        page.locator("li:has-text('Other queries')").click()
        modal.get_by_text("High").click()
        subject = modal.get_by_placeholder("Subject")
        subject.fill("This is the subject generated via automation")
        description = modal.get_by_placeholder("Describe the case")
        description.fill("This is the description generated via automation")
        modal.get_by_role("button", name="Submit Query").click()
        wait_for_message(page, "Query created successfully.")
        time.sleep(1)

        page.on("dialog", lambda dialog:dialog.accept())
        page.get_by_role("button", name="Delete").click()
        wait_for_message(page,"Query deleted successfully.")
        time.sleep(1)
