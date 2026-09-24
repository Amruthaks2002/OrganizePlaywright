from playwright.sync_api import sync_playwright, expect
from utils.login_helper import login


def wait_for_message(page, text, timeout=20000):
    msg = page.get_by_text(text)
    msg.wait_for(state="visible", timeout=timeout)
    return msg


def test_approve_request():
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

        # Open the request
        row.get_by_role("button", name="View", exact=True).click()

        view_modal = page.locator("div.fixed.inset-0").last

        # Approve the existing request
        view_modal.get_by_role("button", name="Approve", exact=True).click()

        # Confirm approval
        confirm_dialog = page.locator("div").filter(
            has_text="Are you sure you want to approve this"
        ).last

        confirm_dialog.get_by_role(
            "button", name="Approve", exact=True
        ).click()

        # Verify success message
        wait_for_message(
            page,
            "work mode request approved.",
            timeout=20000
        )

        browser.close()