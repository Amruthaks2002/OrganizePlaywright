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

        #adding the badge gold

        page.get_by_role("button", name=" Add First Criteria ").first.click()
        inputs = page.locator("input[type='number']")
        inputs.nth(0).fill("90")
        inputs.nth(1).fill("100")
        page.locator("select").select_option("3")
        page.get_by_role("button", name="Add Criteria").nth(1).click()
        time.sleep(5)

        #adding the badge silver
        page.get_by_role("button", name="Add Criteria").first.click()
        page.locator("select").select_option("2")
        inputs = page.locator("input[type='number']")
        inputs.nth(0).fill("70")
        inputs.nth(1).fill("89")
        page.get_by_role("button", name="Add Criteria").nth(1).click()

        #addding the badge bronze
        page.get_by_role("button", name="Add Criteria").last.click()
        page.locator("select").select_option("1")
        inputs = page.locator("input[type='number']")
        inputs.nth(0).fill("50")
        inputs.nth(1).fill("69")
        page.get_by_role("button", name="Add Criteria").nth(1).click()




        time.sleep(5)