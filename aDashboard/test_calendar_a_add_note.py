from playwright.sync_api import sync_playwright
import time
from utils.login_helper import login


def test_add_note():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        login(page)
        page.wait_for_url("**/dashboard**")
        print("Function start")
        day_cell = page.locator("td.fc-day-today a.fc-daygrid-day-number")
        day_cell.scroll_into_view_if_needed()
        print("Scrolled to today’s date")
        day_cell.click()
        print("Clicked today's calendar date")
        page.fill("#note", "Automation note ")
        page.click("//button[text()='Save']")
        time.sleep(2)
        print("✔ test_add_note_to_calendar PASSED")
        success_msg = page.locator("text=note added successfully")
        success_msg.wait_for(timeout=5000)
        print("✔ Note added successfully confirmed")
        browser.close()


