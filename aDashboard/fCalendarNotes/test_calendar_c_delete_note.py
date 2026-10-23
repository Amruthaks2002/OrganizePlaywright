from playwright.sync_api import sync_playwright
from utils.login_helper import login

def test_delete_note():

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False, slow_mo=300)
        page = browser.new_page()
        login(page)

        today_event = page.locator("td.fc-day-today a.fc-event", has_text="Automation note").first
        today_event.click()
        print("Clicked today's note event")
        page.get_by_role("button" , name="Delete").click()
        print("Clicked Delete Note")
        confirm_delete = page.locator("button.bg-red-600.text-white")
        confirm_delete.click()
        success_msg = page.locator("text=Note deleted successfully")
        success_msg.wait_for(timeout=5000)
        print("Note deleted successfully")

        browser.close()


if __name__ == "__main__":
    test_delete_note()



