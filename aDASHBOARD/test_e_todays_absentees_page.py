import time

from playwright.sync_api import sync_playwright, expect
from utils.login_helper import login

def test_today_absentees():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()
        login(page)
        attendance_btn = page.locator("button:has(h3:has-text('Attendance'))")
        attendance_btn.scroll_into_view_if_needed()
        attendance_btn.click()
        print("Clicked Attendance")
        page.get_by_role("link", name=" View Full Attendance ").click()
        expect(page).to_have_url("**/attendance")


