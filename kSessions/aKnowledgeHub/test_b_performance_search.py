from playwright.sync_api import sync_playwright, expect
from utils.login_helper import login
import time

def test_performance_rankings_search_and_details_popup():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()
        login(page)
        page.get_by_test_id("theme-toggle-button").click()

        sessions_btn = page.get_by_test_id("sidebar-parent-sessions")
        expect(sessions_btn).to_be_visible()
        expect(sessions_btn).to_be_enabled()
        sessions_btn.click()

        knowledge_hub = page.get_by_test_id("sidebar-child-knowledge-hub")
        knowledge_hub.scroll_into_view_if_needed()
        knowledge_hub.click()
        time.sleep(2)

        # search the Performance Rankings table for a specific employee
        search = page.get_by_placeholder("Search employees...")
        search.fill("admin")
        time.sleep(1.5)

        rows = page.locator("table tbody tr")
        expect(rows).to_have_count(1)
        row = rows.first
        expect(row).to_contain_text("Admin User")

        # click the row's expand chevron and check that a details popup appears
        chevron = row.locator("svg path[d='M9 5l7 7-7 7']").locator("xpath=..")
        chevron.click()
        time.sleep(1)

        popup = page.locator(".fixed.inset-0.z-50")
        expect(popup).to_be_visible()
        expect(popup).to_contain_text("Admin User")
