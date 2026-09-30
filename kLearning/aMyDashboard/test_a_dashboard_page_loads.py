from playwright.sync_api import sync_playwright, expect
from utils.learning_helper import open_browser, main_content


def test_my_dashboard_page_loads():
    with sync_playwright() as p:
        browser, page = open_browser(p)
        page.get_by_test_id("sidebar-parent-learning").click()
        page.get_by_test_id("sidebar-child-my-dashboard").click()
        page.wait_for_url("**/learning/dashboard")
        main = main_content(page)

        expect(main.get_by_text("My Learning Journey", exact=True)).to_be_visible()
        expect(main.get_by_text(
            "Track your progress, continue where you left off, and complete your assigned learning programs."
        )).to_be_visible()

        browser.close()
