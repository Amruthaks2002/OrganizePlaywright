from playwright.sync_api import sync_playwright, expect
from utils.login_helper import login

def test_filter_policy_work_modes():
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

        # filter by Policy: only rows linked to the "Night" policy should remain
        policy_filter = main.locator("select").nth(0)
        policy_filter.select_option(label="Night")
        page.wait_for_timeout(800)
        rows = main.locator("table tbody tr")
        count = rows.count()
        assert count > 0, "Expected at least one policy work mode for the Night policy"
        for i in range(count):
            expect(rows.nth(i)).to_contain_text("Night")

        policy_filter.select_option(label="Select Policy")
        page.wait_for_timeout(800)

        # create a throwaway blocked entry so the Blocked status filter has a match
        main.get_by_role("button", name="Add Policy Work Mode").click()
        modal = page.locator("div.fixed.inset-0").filter(has_text="Add Policy Work Mode").last
        modal.locator("select").nth(0).select_option(label="Onsite (ons)")
        modal.locator("select").nth(1).select_option(label="mon tue wed leave policy")
        modal.locator("input").nth(0).fill("100")  # Yearly Balance is required
        modal.locator("input").nth(3).uncheck()  # Active checkbox
        modal.get_by_role("button", name="Create").click()
        expect(page.get_by_text("Policy work mode created successfully.")).to_be_visible(timeout=10000)
        page.wait_for_timeout(500)

        status_filter = main.locator("select").nth(1)
        status_filter.select_option(label="Blocked")
        page.wait_for_timeout(800)
        target_row = main.locator("table tbody tr", has_text="mon tue wed leave policy").filter(has_text="Onsite")
        expect(target_row).to_be_visible()
        expect(main.locator("table tbody tr", has_text="Probation")).to_have_count(0)

        status_filter.select_option(label="All")
        page.wait_for_timeout(800)

        # cleanup
        target_row = main.locator("table tbody tr", has_text="mon tue wed leave policy").filter(has_text="Onsite")
        target_row.get_by_role("button", name="Edit").click()
        page.wait_for_timeout(500)  # let the modal's enter transition settle
        edit_modal = page.locator("div.fixed.inset-0").filter(has_text="Edit Policy Work Mode")
        edit_modal.get_by_role("button", name="Delete").first.click(force=True)
        confirm = page.locator("div.fixed.inset-0").filter(has_text="Are you sure").last
        confirm.get_by_role("button", name="Delete").click()
        expect(page.get_by_text("Policy work mode deleted successfully.")).to_be_visible(timeout=10000)

        browser.close()
