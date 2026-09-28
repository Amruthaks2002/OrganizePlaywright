from playwright.sync_api import sync_playwright, expect
from utils.login_helper import login

def test_kra_historical_delete_restricted():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context(viewport={"width": 1600, "height": 900})
        page = context.new_page()
        login(page)
        page.get_by_test_id("theme-toggle-button").click()

        page.get_by_test_id("sidebar-parent-reviews").click()
        page.get_by_test_id("sidebar-child-template-content").click()
        main = page.get_by_test_id("main-content")

        # KRAs that already have review history are flagged so deletion is
        # blocked and existing review records stay intact
        banner = main.get_by_text("This KRA has historical review data. Deletion is restricted to preserve records.")
        expect(banner.first).to_be_visible()

        browser.close()
