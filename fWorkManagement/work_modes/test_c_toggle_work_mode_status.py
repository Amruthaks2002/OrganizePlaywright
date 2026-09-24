from playwright.sync_api import sync_playwright, expect
from utils.login_helper import login

def test_toggle_work_mode_status():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()
        login(page)
        page.get_by_test_id("theme-toggle-button").click()

        page.get_by_test_id("sidebar-parent-work management").click()
        page.get_by_test_id("sidebar-child-work-modes").click()
        main = page.get_by_test_id("main-content")

        # create a throwaway work mode so Onsite/Work From Home stay untouched
        # for other suites (e.g. work_dashboard's Apply Work Mode dropdown)
        main.get_by_role("button", name="Add Work Mode").click()
        modal = page.locator("div.fixed.inset-0").filter(has_text="Add Work Mode").last
        inputs = modal.locator("input")
        inputs.nth(0).fill("Toggle Target Mode")
        inputs.nth(1).fill("TGL")
        modal.get_by_role("button", name="Create").click()
        expect(page.get_by_text("Work mode created successfully.")).to_be_visible(timeout=10000)

        row = main.locator("table tbody tr", has_text="Toggle Target Mode")
        checkbox = row.locator("input[type=checkbox]")
        expect(checkbox).to_be_checked()

        checkbox.click(force=True)
        page.wait_for_timeout(1000)
        expect(checkbox).not_to_be_checked()

        checkbox.click(force=True)
        page.wait_for_timeout(1000)
        expect(checkbox).to_be_checked()

        # cleanup
        row.get_by_role("button", name="Edit").click()
        page.wait_for_timeout(500)  # let the modal's enter transition settle
        edit_modal = page.locator("div.fixed.inset-0").filter(has_text="Edit Work Mode")
        edit_modal.get_by_role("button", name="Delete").first.click(force=True)
        confirm = page.locator("div.fixed.inset-0").filter(has_text="Are you sure").last
        confirm.get_by_role("button", name="Delete").click()
        expect(page.get_by_text("Work mode deleted successfully.")).to_be_visible(timeout=10000)

        browser.close()
