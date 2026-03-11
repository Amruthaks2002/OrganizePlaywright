from playwright.sync_api import sync_playwright


def test_delete_note():

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False, slow_mo=300)
        page = browser.new_page()
        page.goto("https://organice.qc.iocod.com")
        page.fill("#email", "admin@example.com")
        page.fill("#password", "password")
        page.click("[data-testid='sign-in-button']")
        page.wait_for_url("**/dashboard**")
        print("✔ Logged in successfully")
        page.get_by_role("button", name="Celebrations On").click()

        today_event = page.locator("td.fc-day-today a.fc-event").first
        today_event.click()
        print("✔ Clicked today's note event")
        delete_btn = page.locator("//button[normalize-space()='Delete Note']")
        delete_btn.wait_for(state="visible", timeout=5000)
        delete_btn.click()
        print("✔ Clicked Delete Note")
        confirm_delete = page.locator("button.bg-red-600.text-white")
        confirm_delete.click()
        success_msg = page.locator("text=Note deleted successfully")
        success_msg.wait_for(timeout=5000)

        print("✔ Note deleted successfully")

        page.wait_for_timeout(2000)

        browser.close()

