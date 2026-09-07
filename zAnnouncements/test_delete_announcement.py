from playwright.sync_api import sync_playwright
import time


def test_newannouncement():

    with sync_playwright() as p:

        # Launch browser
        browser = p.chromium.launch(headless=False, slow_mo=500)
        context = browser.new_context()
        page = context.new_page()

        # ---------------------------------------------------------
        # OPEN WEBSITE
        # ---------------------------------------------------------
        page.goto("https://organice.qc.iocod.com")
        page.wait_for_selector("#email")

        # ---------------------------------------------------------
        # LOGIN
        # ---------------------------------------------------------
        page.fill("#email", "admin@example.com")
        page.fill("#password", "password")

        page.click("[data-testid='sign-in-button']")
        page.wait_for_url("**/dashboard")
        print("✔ Logged in successfully")



        # ---------------------------------------------------------
        # OPEN ANNOUNCEMENTS
        # ---------------------------------------------------------
        page.click('button[data-testid="announcements-button"]')
        time.sleep(1)

        page.click("text=View all announcements")
        page.wait_for_url("**/announcements/manage")

        print("✔ Navigated to Announcements page")

        # ---------------------------------------------------------
        # SELECT ALL CHECKBOX
        # ---------------------------------------------------------
        select_all = page.locator("label:has-text('Select All')")
        select_all.wait_for()
        select_all.click(force=True)

        print("✔ Clicked Select All")


        # ---------------------------------------------------------
        # HANDLE ALERT
        # ---------------------------------------------------------
        # ---------------------------------------------------------
        # DELETE SELECTED (CORRECT)
        # ---------------------------------------------------------

        # Attach dialog handler FIRST
        page.once("dialog", lambda dialog: dialog.accept())

        delete_btn = page.locator("//button[.//span[text()='Delete Selected']]")
        delete_btn.wait_for(state="visible")
        delete_btn.click(force=True)

        print("✔ Clicked Delete Selected and accepted alert")

        time.sleep(2)
