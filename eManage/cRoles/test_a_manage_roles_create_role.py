from playwright.sync_api import sync_playwright
import time
from utils.login_helper import login

def wait_for_message(page, text , timeout=10000):
    msg = page.get_by_text(text)
    msg.wait_for(state="visible" , timeout=timeout)
    return msg

def test_create_role():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()
        login(page)
        page.get_by_test_id("sidebar-parent-manage").click()
        page.get_by_test_id("sidebar-child-roles").click()
        page.locator("#name").fill("Automation Role")

        import random

        boxes = page.locator("input[data-testid='checkbox']")
        for cb in random.sample(boxes.all(), 3):
            cb.check()

        page.get_by_role("button", name="Create Role").click()
        time.sleep(5)
        wait_for_message(page,"Role created successfully.")
        print("success message appeared")




