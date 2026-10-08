from playwright.sync_api import sync_playwright, expect
from utils.login_helper import login

def test_filter_by_search_employee():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()
        login(page)
        page.get_by_test_id("theme-toggle-button").click()

        page.get_by_test_id("sidebar-parent-work management").click()
        page.get_by_test_id("sidebar-child-work-summary").click()
        main = page.get_by_test_id("main-content")

        main.get_by_role("button", name="Log Hours").click()
        page.wait_for_timeout(500)  # let the modal's enter transition settle
        modal = page.locator("div.fixed.inset-0:visible").filter(has_text="Log Working Hours").first
        modal.locator("select").select_option(label="project Beta")
        modal.locator("input[type=number]").fill("1")
        modal.locator("textarea").fill("Auto test E")
        modal.get_by_role("button", name="Log Hours").click()
        expect(page.get_by_text("Working hours logged successfully.")).to_be_visible(timeout=10000)

        main.get_by_role("button", name="Regular Hours").click()
        page.wait_for_timeout(1500)

        search_input = main.locator("input[placeholder*='Search employee']")
        listbox = page.locator("#vs1__listbox")

        search_input.click()
        search_input.fill("Admin")
        page.wait_for_timeout(1000)
        listbox.get_by_role("option", name="Admin User").click()
        page.wait_for_timeout(1000)

        row = main.locator("table tbody tr", has_text="Auto test E")
        expect(row).to_be_visible()

        # searching for a different employee with no logged hours filters the row out
        main.locator(".vs__clear").click(force=True)
        page.wait_for_timeout(500)
        search_input.click()
        search_input.fill("Abdul Hafeelu")
        page.wait_for_timeout(1000)
        listbox.get_by_role("option", name="Abdul Hafeelu").click()
        page.wait_for_timeout(1000)
        expect(main.locator("table tbody tr", has_text="Auto test E")).to_have_count(0)

        main.locator(".vs__clear").click(force=True)
        page.wait_for_timeout(1000)

        # cleanup
        row = main.locator("table tbody tr", has_text="Auto test E")
        row.locator("td").last.locator("button").last.click()
        page.wait_for_timeout(500)
        confirm = page.locator("div.fixed.inset-0:visible").filter(has_text="Delete Work Log").first
        confirm.get_by_role("button", name="Delete").click()
        expect(page.get_by_text("Working hours deleted successfully.")).to_be_visible(timeout=10000)

        browser.close()
