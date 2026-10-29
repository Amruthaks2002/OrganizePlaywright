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
        time.sleep(2)

        start_date = page.locator("input[type=date]").nth(0)
        end_date = page.locator("input[type=date]").nth(1)

        page.get_by_role("button" , name="Today").click()
        expect(start_date).to_have_value(end_date.input_value())

        page.get_by_role("button" , name = "This Week").click()
        assert start_date.input_value() != end_date.input_value(), "This Week did not widen the date range."

        page.get_by_role("button" , name = "This Month").click()
        time.sleep(2)
        page.get_by_placeholder("All Types").fill("other")
        page.locator("li:has-text('Other queries')").click()

        # Status is a multi-select that defaults to Open + In Progress;
        # deselect In Progress to filter down to Open only.
        page.get_by_role("button", name="Deselect In Progress").click()

        priority = page.locator("select.people-portal-input").nth(1)
        priority.select_option("Medium")
        time.sleep(2)
        page.get_by_role("button" , name = "Apply").click()
        time.sleep(2)