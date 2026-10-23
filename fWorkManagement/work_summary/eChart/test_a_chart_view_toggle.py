from playwright.sync_api import sync_playwright, expect
from utils.login_helper import login

def test_chart_view_toggle():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()
        login(page)
        page.get_by_test_id("theme-toggle-button").click()

        page.get_by_test_id("sidebar-parent-work management").click()
        page.get_by_test_id("sidebar-child-work-summary").click()
        main = page.get_by_test_id("main-content")

        # Chart View is the default tab
        expect(main.get_by_role("button", name="Team Hours")).to_be_visible()
        expect(main.get_by_role("button", name="My Hours")).to_be_visible()

        main.get_by_role("button", name="Team Hours").click()
        page.wait_for_timeout(1500)
        expect(main.get_by_text("Team Weekly Hours (All Teams)")).to_be_visible()

        main.get_by_role("button", name="My Hours").click()
        page.wait_for_timeout(1500)
        expect(main.get_by_text("Team Weekly Hours (All Teams)")).to_have_count(0)
        expect(main).to_contain_text("Weekly Hours")

        browser.close()
