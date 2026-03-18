from playwright.sync_api import sync_playwright, expect
from utils.login_helper import login
import time


def wait_for_message(page, text, timeout=10000):
    msg = page.get_by_text(text)
    msg.wait_for(state="visible", timeout=timeout)
    return msg


def test_celebration_photo():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()
        login(page)
        page.get_by_test_id("theme-toggle-button").click()

        page.get_by_test_id("sidebar-navlink-mail template editor").click()
        page.locator("#mail-live-editor-template-695b4128bab267603507c838").click()
        page.locator("#mail-live-editor-btn-bulk-actions").click()
        page.locator("#mail-live-editor-btn-duplicate").click()
        page.locator("#mail-live-editor-modal-add-btn-create").click()
        wait_for_message(page, "Template created successfully!")
        time.sleep(2)
