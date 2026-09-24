from playwright.sync_api import sync_playwright, expect
from utils.login_helper import login

def test_delete_policy_work_mode():
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

        main.get_by_role("button", name="Add Policy Work Mode").click()
        modal = page.locator("div.fixed.inset-0").filter(has_text="Add Policy Work Mode").last
        modal.locator("select").nth(0).select_option(label="Work From Home (wfh)")
        modal.locator("select").nth(1).select_option(label="mon tue wed leave policy")
        modal.locator("input").nth(0).fill("100")  # Yearly Balance is required
        modal.get_by_role("button", name="Create").click()
        expect(page.get_by_text("Policy work mode created successfully.")).to_be_visible(timeout=10000)
        page.wait_for_timeout(500)

        row = main.locator("table tbody tr", has_text="mon tue wed leave policy").filter(has_text="Work From Home")
        row.get_by_role("button", name="Edit").click()
        edit_modal = page.locator("div.fixed.inset-0").filter(has_text="Edit Policy Work Mode")
        edit_modal.get_by_role("button", name="Delete").first.click(force=True)

        # cancelling the confirmation should leave the record in place and
        # close the confirmation only, so the edit modal underneath must be
        # dismissed too before it can be reopened
        confirm = page.locator("div.fixed.inset-0").filter(has_text="Are you sure").last
        confirm.get_by_role("button", name="Cancel").click()
        page.wait_for_timeout(300)
        edit_modal.get_by_role("button", name="Cancel").click()
        page.wait_for_timeout(500)
        expect(row).to_be_visible()

        row.get_by_role("button", name="Edit").click()
        edit_modal = page.locator("div.fixed.inset-0").filter(has_text="Edit Policy Work Mode")
        edit_modal.get_by_role("button", name="Delete").first.click(force=True)
        confirm = page.locator("div.fixed.inset-0").filter(has_text="Are you sure").last
        confirm.get_by_role("button", name="Delete").click()

        expect(page.get_by_text("Policy work mode deleted successfully.")).to_be_visible(timeout=10000)
        expect(main.locator("table tbody tr", has_text="mon tue wed leave policy").filter(has_text="Work From Home")).to_have_count(0)

        browser.close()
