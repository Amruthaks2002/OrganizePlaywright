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

def test_apply_leave():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()

        #login to employees dashboard
        login(page)
        page.get_by_test_id("theme-toggle-button").click()

        #apply full day leave
        page.get_by_test_id("sidebar-navlink-leave dashboard").click()
        page.get_by_role("button", name=" Apply Leave ").click()
        from datetime import datetime
        today = datetime.today().day
        page.locator("button:has(span:text-is('{}'))".format(today)).click()
        page.locator("select").select_option(label="Sick Leave")
        page.get_by_placeholder("Please provide details about your leave request...").fill("Feeling unwell")
        page.get_by_role("button", name="Get AI Suggestions").click()
        page.locator("div.max-h-60 button").first.click()
        page.locator("input[type='file']").set_input_files("/Users/amruthaks/Downloads/supporting docu.png")
        page.get_by_role("button" , name="Submit Request").click()
        wait_for_message(page, "Leave application submitted successfully.")
        time.sleep(2)

        #cancel the applied leave
        page.get_by_role("button", name=" Apply Leave ").click()
        page.locator("button:has(span:text-is('S'))").click()
        page.get_by_role("button", name=" Cancel This Request ").click()
        page.get_by_role("button", name="Yes, Cancel").click()
        wait_for_message(page, "Request cancelled successfully.")
        time.sleep(2)

        #apply leave for half day
        page.get_by_role("button", name=" Apply Leave ").click()
        from datetime import datetime
        today = datetime.today().day
        page.locator("button:has(span:text-is('{}'))".format(today)).click()
        page.locator("select").select_option(label="Sick Leave")
        page.locator("label:has(input[value='half'])").click()
        page.locator("label:has-text('First Session')").click()
        page.get_by_placeholder("Please provide details about your leave request...").fill("Feeling unwell")
        page.get_by_role("button", name="Get AI Suggestions").click()
        page.locator("div.max-h-60 button").first.click()
        page.locator("input[type='file']").set_input_files("/Users/amruthaks/Downloads/supporting docu.png")
        page.get_by_role("button", name="Submit Request").click()
        wait_for_message(page, "Leave application submitted successfully.")
        time.sleep(2)




