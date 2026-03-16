from playwright.sync_api import sync_playwright, expect
from utils.login_helper import login
import time

def wait_for_message(page,text,timeout=10000):
    msg= page.get_by_text(text)
    msg.wait_for(state="visible",timeout=timeout)
    return msg

def test_designation_creation():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()
        login(page)

        #editing and changing the status to cancel

        page.get_by_test_id("theme-toggle-button").click()
        page.get_by_test_id("sidebar-navlink-people portal").click()
        page.get_by_role("button", name="Edit").first.click()
        modal = page.locator("div:has(h3:has-text('Edit Query'))")
        modal.locator("label:has-text('Cancelled')").click()
        page.get_by_role("button", name="Save Changes").click()
        wait_for_message(page,"Query updated successfully.")
        time.sleep(1)

        #applying filters to get the cancelled query

        page.locator(".vs__dropdown-toggle").nth(1).click()
        page.locator("input.vs__search").nth(1).fill("open")
        page.locator("li:has-text('Open')").click()


        time.sleep(2)

        page.locator("input.vs__search").nth(1).fill("cancel")
        page.locator("li:has-text('Cancelled')").click()

        page.get_by_role("button", name="Apply").click()

        #checking if the table has the cancelled query after applying the filters

        table = page.locator("table")
        expect(table).to_contain_text("generated via automation")

        #changing the query status again from cancelled to open

        page.get_by_role("button", name="Edit").first.click()
        modal = page.locator("div:has(h3:has-text('Edit Query'))")
        modal.locator("label:has-text('Open')").click()
        page.get_by_role("button", name="Save Changes").click()
        wait_for_message(page, "Query updated successfully.")
        time.sleep(2)

        #resetting the filters

        page.get_by_role("button", name="Reset").click()
        time.sleep(2)


