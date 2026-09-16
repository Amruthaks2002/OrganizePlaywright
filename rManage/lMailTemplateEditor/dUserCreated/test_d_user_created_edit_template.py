from playwright.sync_api import sync_playwright, expect
from utils.login_helper import login
from datetime import datetime
import time


def wait_for_message(page, text, timeout=10000):
    msg = page.get_by_text(text)
    msg.wait_for(state="visible", timeout=timeout)
    return msg


def test_user_created_edit_template():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()
        login(page)
        page.get_by_test_id("theme-toggle-button").click()

        page.get_by_test_id("sidebar-parent-manage").click()
        mail_link = page.get_by_test_id("sidebar-child-mail-template-editor")
        mail_link.wait_for(state="visible")
        mail_link.click()
        page.wait_for_url("**/live-email-editor**")

        # reload to pick up a fresh CSRF token before the mutating actions below
        page.reload()
        time.sleep(2)

        page.locator("#vs1__combobox").click()
        page.get_by_role("option", name="User Created").click()
        time.sleep(1)

        # duplicate a template first so editing doesn't disturb the real active one
        template = page.locator("[id^='mail-live-editor-template-']").first
        template.click()
        time.sleep(1)

        page.locator("#mail-live-editor-btn-bulk-actions").click()
        page.locator("#mail-live-editor-btn-duplicate").wait_for(state="visible")
        page.locator("#mail-live-editor-btn-duplicate").click()

        create_btn = page.locator("#mail-live-editor-modal-add-btn-create")
        create_btn.wait_for(state="visible")
        create_btn.click()
        wait_for_message(page, "Template created successfully!")
        time.sleep(2)

        duplicated_template = page.locator("[id^='mail-live-editor-template-']").last
        duplicated_template.click()
        time.sleep(1)

        page.locator("#mail-live-editor-btn-edit").click()
        time.sleep(1)

        name_input = page.locator("#mail-live-editor-input-name")
        name_input.fill("")
        name_input.fill(f"Automated edited template {datetime.now().strftime('%H%M%S')}")

        page.locator("#mail-live-editor-btn-save").click()
        wait_for_message(page, "Template saved successfully!")
        time.sleep(2)

        browser.close()
