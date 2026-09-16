from playwright.sync_api import sync_playwright
import time
from utils.login_helper import login

def wait_for_message(page,text,timeout=10000):
    msg = page.get_by_text(text)
    msg.wait_for(state = "visible" , timeout=timeout)
    return msg

def test_delete_role():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page = browser.new_page()
        login(page)
        page.get_by_test_id("theme-toggle-button").click()

        page.get_by_test_id("sidebar-parent-manage").click()
        page.get_by_test_id("sidebar-child-roles").click()

        role_card = page.get_by_text("automation role", exact=False) \
            .locator("xpath=ancestor::div[contains(@class,'justify-between')][1]")
        role_card.wait_for(state="visible")

        # Click Delete (second of the two icon-only action buttons on the card)
        role_card.locator("button").nth(1).click()
        modal = page.get_by_role("heading", name="Delete Role").locator("xpath=ancestor::div[contains(@class,'fixed')][1]")
        modal.wait_for()
        modal.get_by_role("button", name="Delete", exact=True).click()
        time.sleep(2)

        wait_for_message(page,"Role deleted successfully.")
        print("Role deleted successfully.")



