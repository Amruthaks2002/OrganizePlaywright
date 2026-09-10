import time
from playwright.sync_api import sync_playwright
from utils.login_helper import login

def test_edit_note():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False, slow_mo=300)
        page = browser.new_page()
        login(page)

        today_event = page.locator("td.fc-day-today a.fc-event").first
        today_event.click()
        print("✔ Clicked today's note event")
        note_box = page.locator("#note")
        note_box.wait_for()

        note_box.fill("Automation note edited")
        save_btn = page.locator("//button[normalize-space()='Save']")
        save_btn.wait_for()
        save_btn.click()

        print("✔ Note updated successfully")

        success_msg = page.locator("text=note updated successfully")
        success_msg.wait_for(timeout=5000)
        browser.close()


if __name__ == "__main__":
    test_edit_note()

