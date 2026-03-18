from playwright.sync_api import sync_playwright, expect
from utils.login_helper import login
import time

def wait_for_message(page,text,timeout=10000):
    msg= page.get_by_text(text)
    msg.wait_for(state="visible",timeout=timeout)
    return msg

def test_celebration_photo():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()
        login(page)
        page.get_by_test_id("theme-toggle-button").click()

        page.get_by_test_id("sidebar-navlink-mail template editor").click()
        page.locator("#mail-live-editor-event-type-leave_submitted").click()
        page.locator("#mail-live-editor-btn-add-template").click()
        page.get_by_placeholder("e.g., Professional Leave Notification").fill("Automated leave submitted template")
        page.locator("#mail-live-editor-modal-add-input-subject").fill("Automated subject")
        page.locator("#mail-live-editor-modal-add-input-body").fill("Automated email body")
        create_btn = page.locator("#mail-live-editor-modal-add-btn-create")
        expect(create_btn).to_be_visible()
        create_btn.click()
        wait_for_message(page,"Template created successfully!")






