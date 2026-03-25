import time
from playwright.sync_api import sync_playwright, expect
from utils.login_helper import login

def test_present_count():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()
        login(page)
        page.get_by_test_id("theme-toggle-button").click()

        attendance_btn = page.locator("button:has(h3:has-text('Attendance'))")
        attendance_btn.scroll_into_view_if_needed()
        attendance_btn.click()
        print("Clicked Attendance")

        def get_count(label):
            locator = page.locator(f"p:has-text('{label}')").locator("xpath=following-sibling::p[1]")
            expect(locator).to_be_visible()
            return int(locator.inner_text())

        total = get_count("Total Employees")
        present = get_count("Present Today")
        on_leave = get_count("On Leave")
        in_office = get_count("In Office")
        remote = get_count("Working Remotely")

        print("Total Employees:", total)
        print("Present Today:", present)
        print("On Leave:", on_leave)
        print("In Office:", in_office)
        print("Working Remotely:", remote)

        time.sleep()

        # validations
        assert total - on_leave == present
        assert present - remote == in_office

        print("\n✔ Attendance numbers verified successfully")

        browser.close()



