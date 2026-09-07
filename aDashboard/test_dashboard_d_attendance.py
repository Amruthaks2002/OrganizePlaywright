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
        remote = get_count("In Work Mode")

        print("Total Employees:", total)
        print("Present Today:", present)
        print("On Leave:", on_leave)
        print("In Office:", in_office)
        print("Working Remotely:", remote)

        # validations
        assert total - on_leave == present
        assert in_office + remote + on_leave == total

        # No negative values
        assert total >= 0
        assert present >= 0
        assert on_leave >= 0
        assert in_office >= 0
        assert remote >= 0

        # Present can't exceed total
        assert present <= total

        # On leave can't exceed total
        assert on_leave <= total

        # In office and remote can't exceed present
        assert in_office <= present
        assert remote <= present

        print("\n✔ Attendance numbers verified successfully")

        browser.close()



