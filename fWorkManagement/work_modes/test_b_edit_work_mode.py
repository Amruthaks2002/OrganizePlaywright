from playwright.sync_api import sync_playwright, expect
from utils.login_helper import login

def test_edit_work_mode():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()
        login(page)
        page.get_by_test_id("theme-toggle-button").click()

        page.get_by_test_id("sidebar-parent-work management").click()
        page.get_by_test_id("sidebar-child-work-modes").click()
        main = page.get_by_test_id("main-content")

        # create a work mode to edit
        main.get_by_role("button", name="Add Work Mode").click()
        modal = page.locator("div.fixed.inset-0").filter(has_text="Add Work Mode").last
        inputs = modal.locator("input")
        inputs.nth(0).fill("Edit Target Mode")
        inputs.nth(1).fill("EDIT")
        modal.get_by_role("button", name="Create").click()
        expect(page.get_by_text("Work mode created successfully.")).to_be_visible(timeout=10000)

        row = main.locator("table tbody tr", has_text="Edit Target Mode")
        row.get_by_role("button", name="Edit").click()
        page.wait_for_timeout(500)  # let the modal's enter transition settle
        edit_modal = page.locator("div.fixed.inset-0").filter(has_text="Edit Work Mode")
        edit_inputs = edit_modal.locator("input")
        edit_inputs.nth(0).fill("Edit Target Mode Updated")
        edit_modal.get_by_role("button", name="Update").first.click()

        expect(page.get_by_text("Work mode updated successfully.")).to_be_visible(timeout=10000)
        updated_row = main.locator("table tbody tr", has_text="Edit Target Mode Updated")
        expect(updated_row).to_be_visible()

        # the edit modal takes a moment to finish closing after Update; reopening
        # it too soon can hit its old Delete button mid-teardown and detach the click
        expect(page.locator("div.fixed.inset-0").filter(has_text="Edit Work Mode")).to_have_count(0, timeout=8000)

        # cleanup
        updated_row.get_by_role("button", name="Edit").click()
        page.wait_for_timeout(500)  # let the modal's enter transition settle
        cleanup_modal = page.locator("div.fixed.inset-0").filter(has_text="Edit Work Mode")
        cleanup_modal.get_by_role("button", name="Delete").first.click(force=True)
        confirm = page.locator("div.fixed.inset-0").filter(has_text="Are you sure").last
        confirm.get_by_role("button", name="Delete").click()
        expect(page.get_by_text("Work mode deleted successfully.")).to_be_visible(timeout=10000)

        browser.close()
