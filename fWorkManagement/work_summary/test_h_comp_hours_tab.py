from playwright.sync_api import sync_playwright, expect
from utils.login_helper import login

def test_comp_hours_tab():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()
        login(page)
        page.get_by_test_id("theme-toggle-button").click()

        page.get_by_test_id("sidebar-parent-work management").click()
        page.get_by_test_id("sidebar-child-work-summary").click()
        main = page.get_by_test_id("main-content")

        main.get_by_role("button", name="Comp Hours").click()
        page.wait_for_timeout(1500)

        # Comp Hours adds a Status filter and Export action on top of the
        # Regular Hours columns, plus a dedicated Comp Off Status column
        expect(main.get_by_text("Status", exact=True)).to_be_visible()
        status_filter = main.locator("select").last
        expect(status_filter).to_be_visible()
        expect(status_filter.locator("option", has_text="Pending")).to_have_count(1)
        expect(status_filter.locator("option", has_text="Approved")).to_have_count(1)
        expect(status_filter.locator("option", has_text="Rejected")).to_have_count(1)

        expect(main.get_by_role("button", name="Export")).to_be_visible()
        expect(main.locator("table thead")).to_contain_text("Comp Off Status")

        browser.close()
