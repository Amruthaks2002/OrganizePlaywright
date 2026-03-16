from os import name

from playwright.sync_api import Page, expect
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

def test_query_filters():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()
        login(page)
        page.get_by_test_id("theme-toggle-button").click()
        page.get_by_test_id("sidebar-navlink-people portal").click()
        page.get_by_role("button" , name="Today").click()
        expect(page.get_by_text("generated via automation"))
        page.get_by_role("button" , name = "This Week").click()
        expect(page.get_by_text("generated via automation"))
        page.get_by_role("button" , name = "This Month").click()
        time.sleep(2)
        page.get_by_placeholder("All Types").fill("other")
        page.locator("li:has-text('Other queries')").click()
        status = page.locator("select.people-portal-input").first
        status.wait_for()
        status.select_option("open")
        priority = page.locator("select.people-portal-input").nth(1)
        priority.select_option("Medium")
        time.sleep(2)
        page.get_by_role("button" , name = "Apply").click()
        time.sleep(2)