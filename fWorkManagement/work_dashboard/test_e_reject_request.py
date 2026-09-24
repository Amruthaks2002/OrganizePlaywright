from playwright.sync_api import sync_playwright, expect
from utils.login_helper import login


def wait_for_message(page, text, timeout=20000):
    msg = page.get_by_text(text)
    msg.wait_for(state="visible", timeout=timeout)
    return msg


def test_reject_request():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()

        login(page)

        page.get_by_test_id("theme-toggle-button").click()

        page.get_by_test_id("sidebar-parent-work management").click()
        page.get_by_test_id("sidebar-child-work-dashboard").click()

        main = page.get_by_test_id("main-content")

        # Use the already existing pending request
        row = main.locator('table:has-text("EMPLOYEE") tbody tr').first

        # Open the existing request
        row.get_by_role("button", name="View", exact=True).click()

        view_modal = page.locator("div.fixed.inset-0").last

        # Click Reject
        view_modal.get_by_role("button", name="Reject", exact=True).click()

        # Enter rejection reason
        page.get_by_placeholder(
            "Please provide a reason to reject..."
        ).fill("Rejected by automation")

        # Submit rejection
        reject_form = page.locator("form").filter(
            has_text="Reason to Reject"
        )

        reject_form.get_by_role(
            "button", name="Reject", exact=True
        ).click()

        # Verify rejection success message
        wait_for_message(
            page,
            "work mode request rejected.",
            timeout=20000
        )


        browser.close()