from playwright.sync_api import sync_playwright, expect
from utils.login_helper import login

def test_no_active_template_error():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context(viewport={"width": 1600, "height": 900})
        page = context.new_page()
        login(page)
        page.get_by_test_id("theme-toggle-button").click()

        page.get_by_test_id("sidebar-parent-reviews").click()
        page.get_by_test_id("sidebar-child-team-reviews").click()
        main = page.get_by_test_id("main-content")

        # the first team member card (Admin User / System Administrator) has
        # no active review template for its designation
        main.get_by_role("button", name="Review", exact=True).first.click()
        page.wait_for_timeout(1500)

        expect(page.get_by_text("No active review template found for this designation.")).to_be_visible(timeout=10000)
        expect(main).to_contain_text("Not Rated")

        browser.close()
