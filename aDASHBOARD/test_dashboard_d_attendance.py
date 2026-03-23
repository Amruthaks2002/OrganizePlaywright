from playwright.sync_api import sync_playwright, expect

def test_present_count():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()
        page.goto("https://organice.qc.iocod.com")
        page.fill("#email", "admin@example.com")
        page.fill("#password", "password")
        page.locator("[data-testid='sign-in-button']").click()
        page.wait_for_url("**/dashboard")
        attendance_btn = page.locator(
            "button:has(h3:has-text('Attendance'))"
        )
        attendance_btn.scroll_into_view_if_needed()
        attendance_btn.click()
        print("✔ Clicked Attendance button")
        def get_value(label):
            locator = page.locator(
                f"span:has-text('{label}') >> xpath=following-sibling::span[contains(@class,'font-bold')]"
            )
            expect(locator).to_be_visible()
            return int(locator.inner_text())
        total = get_value("Total employees")
        present = get_value("Present today")
        absent = get_value("Absent today")
        print(f"Total: {total}")
        print(f"Present: {present}")
        print(f"Absent: {absent}")
        assert present == total - absent
        print("\n✔ test_employee_present_count PASSED")
        browser.close()


