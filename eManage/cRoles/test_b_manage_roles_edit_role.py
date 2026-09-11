import time

from playwright.sync_api import sync_playwright
from utils.login_helper import login

def wait_for_message(page, text, timeout = 10000):
    msg = page.get_by_text(text)
    msg.wait_for(state="visible" , timeout=timeout)
    return msg

def test_edit_role():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()

        login(page)
        page.get_by_test_id("theme-toggle-button").click()

        page.get_by_test_id("sidebar-parent-manage").click()
        page.get_by_test_id("sidebar-child-roles").click()
        page.get_by_text("automation role", exact=False).wait_for()

        role_card = page.get_by_text("automation role", exact=False) \
                        .locator("xpath=ancestor::div[contains(@class,'justify-between')][1]")
        role_card.wait_for(state="visible")

        # Click Edit (first of the two icon-only action buttons on the card)
        role_card.locator("button").nth(0).click()
        modal = page.locator("div.fixed.inset-0").filter(has_text="Edit Role").first
        modal.wait_for()
        edit_input = modal.locator("form").locator("input").first
        edit_input.fill("Automation Role edited")

        print("Filled role name successfully")

        modal.get_by_role("button", name="Save Changes").click()
        time.sleep(3)

        wait_for_message(page,"Role updated successfully.")
        print("Role edited successfully")


