from playwright.sync_api import sync_playwright, expect
from utils.learning_helper import open_browser, main_content


def test_no_enrollments_empty_state():
    with sync_playwright() as p:
        browser, page = open_browser(p)
        page.get_by_test_id("sidebar-parent-learning").click()
        page.get_by_test_id("sidebar-child-my-dashboard").click()
        page.wait_for_url("**/learning/dashboard")
        main = main_content(page)

        # the admin user isn't enrolled in any program by default
        expect(main.get_by_text("No active enrollments")).to_be_visible()
        expect(main.get_by_text("You haven't been assigned to any learning journeys yet.")).to_be_visible()
        expect(main.get_by_text("My Learning Journeys")).to_have_count(0)

        browser.close()
