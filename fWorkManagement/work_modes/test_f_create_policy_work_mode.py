from playwright.sync_api import sync_playwright, expect
from utils.login_helper import login

def test_create_policy_work_mode():
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
        modal.locator("select").nth(0).select_option(label="Onsite (ons)")
        modal.locator("select").nth(1).select_option(label="mon tue wed leave policy")
        inputs = modal.locator("input")
        inputs.nth(0).fill("240")
        inputs.nth(1).fill("3")
        inputs.nth(2).fill("5")
        modal.get_by_text("Description (Optional)").click()
        modal.locator("textarea").first.fill("Automated test policy work mode")
        modal.get_by_role("button", name="Create").click()

        expect(page.get_by_text("Policy work mode created successfully.")).to_be_visible(timeout=10000)
        row = main.locator("table tbody tr", has_text="mon tue wed leave policy").filter(has_text="Onsite")
        expect(row).to_be_visible()
        expect(row).to_contain_text("240")
        expect(row).to_contain_text("3")

        # cleanup
        row.get_by_role("button", name="Edit").click()
        page.wait_for_timeout(500)  # let the modal's enter transition settle
        edit_modal = page.locator("div.fixed.inset-0").filter(has_text="Edit Policy Work Mode")
        edit_modal.get_by_role("button", name="Delete").first.click(force=True)
        confirm = page.locator("div.fixed.inset-0").filter(has_text="Are you sure").last
        confirm.get_by_role("button", name="Delete").click()
        expect(page.get_by_text("Policy work mode deleted successfully.")).to_be_visible(timeout=10000)

        browser.close()
