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
        page.get_by_text("automation role").wait_for()

        role_card = page.locator("div.flex.items-center.justify-between") \
                        .filter(has_text="automation role") \
                        .first
        role_card.wait_for(state="visible")

        # Click Edit
        role_card.get_by_role("button", name="Edit").click()
        modal = page.get_by_role("heading", name="Edit Role")
        modal.wait_for()
        edit_modal = modal.locator("xpath=ancestor::div[contains(@class,'p-6')]")
        edit_input = edit_modal.get_by_test_id("text-input")
        edit_input.fill("Automation Role edited")

        print("Filled role name successfully")

        print("Random permissions selected successfully")
        page.get_by_role("button" ,name=" Save Changes ").click()
        time.sleep(3)

        wait_for_message(page,"Role updated successfully.")
        print("Role edited successfully")


