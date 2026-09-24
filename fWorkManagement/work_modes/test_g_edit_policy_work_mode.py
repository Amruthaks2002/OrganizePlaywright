from playwright.sync_api import sync_playwright, expect
from utils.login_helper import login

def test_edit_policy_work_mode():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()
        login(page)
        page.get_by_test_id("theme-toggle-button").click()

        page.get_by_test_id("sidebar-parent-work management").click()
        page.get_by_test_id("sidebar-child-work-modes").click()
        main = page.get_by_test_id("main-content")
        main.get_by_role("button", name="Policy Work Modes").click()
        page.wait_for_timeout(1000)

        # create a policy work mode to edit
        main.get_by_role("button", name="Add Policy Work Mode").click()
        modal = page.locator("div.fixed.inset-0").filter(has_text="Add Policy Work Mode").last
        modal.locator("select").nth(0).select_option(label="Work From Home (wfh)")
        modal.locator("select").nth(1).select_option(label="mon tue wed leave policy")
        inputs = modal.locator("input")
        inputs.nth(0).fill("240")
        inputs.nth(1).fill("3")
        inputs.nth(2).fill("5")
        modal.get_by_role("button", name="Create").click()
        expect(page.get_by_text("Policy work mode created successfully.")).to_be_visible(timeout=10000)
        page.wait_for_timeout(500)

        row = main.locator("table tbody tr", has_text="mon tue wed leave policy").filter(has_text="Work From Home")
        row.get_by_role("button", name="Edit").click()
        page.wait_for_timeout(500)  # let the modal's enter transition settle
        edit_modal = page.locator("div.fixed.inset-0").filter(has_text="Edit Policy Work Mode")
        edit_inputs = edit_modal.locator("input")
        edit_inputs.nth(0).fill("300")
        edit_inputs.nth(1).fill("5")
        edit_modal.get_by_role("button", name="Update").first.click()

        expect(page.get_by_text("Policy work mode updated successfully.")).to_be_visible(timeout=10000)
        expect(row).to_contain_text("300")
        expect(row).to_contain_text("5")

        # the edit modal takes a moment to finish closing after Update; reopening
        # it too soon can hit its old Delete button mid-teardown and detach the click
        expect(page.locator("div.fixed.inset-0").filter(has_text="Edit Policy Work Mode")).to_have_count(0, timeout=8000)

        # cleanup
        row.get_by_role("button", name="Edit").click()
        page.wait_for_timeout(500)  # let the modal's enter transition settle
        cleanup_modal = page.locator("div.fixed.inset-0").filter(has_text="Edit Policy Work Mode")
        cleanup_modal.get_by_role("button", name="Delete").first.click(force=True)
        confirm = page.locator("div.fixed.inset-0").filter(has_text="Are you sure").last
        confirm.get_by_role("button", name="Delete").click()
        expect(page.get_by_text("Policy work mode deleted successfully.")).to_be_visible(timeout=10000)

        browser.close()
