from playwright.sync_api import sync_playwright, expect
from utils.login_helper import login
import time

def wait_for_message(page, text, timeout=10000):
    msg = page.get_by_text(text)
    msg.wait_for(state="visible", timeout=timeout)
    return msg


def test_bank_document():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()
        login(page)
        page.get_by_test_id("theme-toggle-button").click()
        from playwright.sync_api import expect
        sessions_btn = page.get_by_test_id("sidebar-parent-sessions")
        expect(sessions_btn).to_be_visible()
        expect(sessions_btn).to_be_enabled()
        sessions_btn.click()
        page.get_by_role("link", name="Badge Criteria").click()

        # edit the badge gold
        page.get_by_role("button", name=" Edit ").nth(0).click()
        inputs = page.locator("input[type='number']")
        inputs.nth(0).fill("91")
        inputs.nth(1).fill("99")
        page.get_by_role("button", name=" Save Changes ").click()
        expect(page.get_by_text("Badge criteria updated")).to_be_visible()

        #edit back to previous value
        page.get_by_role("button", name=" Edit ").nth(0).click()
        inputs = page.locator("input[type='number']")
        inputs.nth(0).fill("90")
        inputs.nth(1).fill("100")
        page.get_by_role("button", name=" Save Changes ").click()
        expect(page.get_by_text("Badge criteria updated")).to_be_visible()
        time.sleep(2)
