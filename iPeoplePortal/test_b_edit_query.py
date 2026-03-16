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

def test_edit_query():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()
        login(page)
        page.get_by_test_id("theme-toggle-button").click()
        page.get_by_test_id("sidebar-navlink-people portal").click()
        page.get_by_role("button", name="Edit").click()
        modal = page.locator(".fixed.inset-0.z-50")
        modal.wait_for()
        modal.get_by_text("Medium").click()
        subject = modal.get_by_placeholder("Subject")
        subject.fill("This is the edited subject generated via automation")
        description = modal.get_by_placeholder("Describe the case")
        description.fill("This is the edited description generated via automation")
        modal.get_by_role("button" , name="Update Query").click()
        wait_for_message(page, "Query updated successfully.")
        time.sleep(1)