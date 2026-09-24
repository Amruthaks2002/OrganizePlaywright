from playwright.sync_api import sync_playwright, expect
from utils.login_helper import login

def wait_for_message(page, text, timeout=10000):
    msg = page.get_by_text(text)
    msg.wait_for(state="visible", timeout=timeout)
    return msg

def pick_open_day(page, modal):
    # Picks the first open day in the visible month; if the month is full
    # (e.g. repeated test runs already used its slots), advances to the next
    # month via the calendar's own "next" arrow until an open day is found.
    for _ in range(12):
        day_grid = modal.locator("div.grid.grid-cols-7.gap-2").last
        buttons = day_grid.locator("button")
        for i in range(buttons.count()):
            btn = buttons.nth(i)
            cls = btn.get_attribute("class") or ""
            if btn.get_attribute("disabled") is None and not btn.get_attribute("style") and "text-slate-300" not in cls:
                text = btn.inner_text().strip()
                if text.isdigit():
                    btn.click()
                    return text
        modal.locator("div.flex.items-center.justify-between.mb-6 button").nth(1).click()
        page.wait_for_timeout(400)
    raise Exception("No open calendar day found across searched months")

def submit_and_confirm(page, submit_button, success_text, timeout=25000):
    # Submitting can either succeed directly (success toast appears and
    # auto-dismisses within a few seconds) or trigger a "Monthly Limit
    # Exceeded" confirmation dialog first (which can itself take several
    # seconds to appear). Poll for whichever happens first so a fast toast
    # is never missed while waiting on a dialog that isn't coming.
    import time
    submit_button.click()
    limit_dialog = page.get_by_text("Monthly Limit Exceeded")
    success_msg = page.get_by_text(success_text)
    dialog_handled = False
    deadline = time.time() + (timeout / 1000)
    while time.time() < deadline:
        if success_msg.is_visible():
            return
        if not dialog_handled and limit_dialog.is_visible():
            page.get_by_role("button", name="Yes, Proceed").click()
            page.wait_for_timeout(300)
            # a plain click can hang here waiting for the button to be
            # judged "stable"; force bypasses that since it's clickable
            submit_button.click(force=True, timeout=10000)
            dialog_handled = True
            continue
        page.wait_for_timeout(250)
    raise AssertionError(
        f"Timed out waiting for '{success_text}' (or the monthly-limit dialog) to appear"
    )

def test_apply_full_day_work_mode():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()
        login(page)
        page.get_by_test_id("theme-toggle-button").click()

        page.get_by_test_id("sidebar-parent-work management").click()
        page.get_by_test_id("sidebar-child-work-dashboard").click()
        main = page.get_by_test_id("main-content")

        main.get_by_role("button", name="Apply Work Mode").click()
        modal = page.locator("div.fixed.inset-0").last
        modal.locator("select").first.select_option(label="Work From Home")
        pick_open_day(page, modal)

        # Full Day is selected by default
        modal.locator("textarea").fill("Automated test - full day work from home")
        submit_and_confirm(page, modal.get_by_role("button", name="Submit Request"), "Work mode application submitted successfully.")

        # newest request appears first in the table
        row = main.locator('table:has-text("EMPLOYEE") tbody tr').first
        expect(row).to_contain_text("Admin User")
        expect(row).to_contain_text("Work From Home")
        expect(row).to_contain_text("1 day(s)")
        expect(row).to_contain_text("pending")

        browser.close()
