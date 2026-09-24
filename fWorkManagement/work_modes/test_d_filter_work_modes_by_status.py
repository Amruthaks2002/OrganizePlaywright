from playwright.sync_api import sync_playwright, expect
from utils.login_helper import login

def test_filter_work_modes_by_status():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()
        login(page)
        page.get_by_test_id("theme-toggle-button").click()

        page.get_by_test_id("sidebar-parent-work management").click()
        page.get_by_test_id("sidebar-child-work-modes").click()
        main = page.get_by_test_id("main-content")

        # create a throwaway blocked work mode so the Blocked filter has a match
        main.get_by_role("button", name="Add Work Mode").click()
        modal = page.locator("div.fixed.inset-0").filter(has_text="Add Work Mode").last
        inputs = modal.locator("input")
        inputs.nth(0).fill("Filter Target Mode")
        inputs.nth(1).fill("FLT")
        inputs.nth(3).uncheck()  # Active checkbox
        modal.get_by_role("button", name="Create").click()
        expect(page.get_by_text("Work mode created successfully.")).to_be_visible(timeout=10000)

        status_filter = main.locator("select").first

        status_filter.select_option(label="Blocked")
        page.wait_for_timeout(800)
        expect(main.locator("table tbody tr", has_text="Filter Target Mode")).to_be_visible()
        expect(main.locator("table tbody tr", has_text="Onsite")).to_have_count(0)

        status_filter.select_option(label="Active")
        page.wait_for_timeout(800)
        expect(main.locator("table tbody tr", has_text="Filter Target Mode")).to_have_count(0)
        expect(main.locator("table tbody tr", has_text="Onsite")).to_be_visible()

        status_filter.select_option(label="All")
        page.wait_for_timeout(800)
        expect(main.locator("table tbody tr", has_text="Filter Target Mode")).to_be_visible()
        expect(main.locator("table tbody tr", has_text="Onsite")).to_be_visible()

        # cleanup
        row = main.locator("table tbody tr", has_text="Filter Target Mode")
        row.get_by_role("button", name="Edit").click()
        page.wait_for_timeout(500)  # let the modal's enter transition settle
        edit_modal = page.locator("div.fixed.inset-0").filter(has_text="Edit Work Mode")
        edit_modal.get_by_role("button", name="Delete").first.click(force=True)
        confirm = page.locator("div.fixed.inset-0").filter(has_text="Are you sure").last
        confirm.get_by_role("button", name="Delete").click()
        expect(page.get_by_text("Work mode deleted successfully.")).to_be_visible(timeout=10000)

        browser.close()
