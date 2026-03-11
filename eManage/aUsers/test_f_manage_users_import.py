from playwright.sync_api import sync_playwright
from utils.login_helper import login
from pathlib import Path
import time


def test_export_and_import_users():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        login(page)
        page.get_by_test_id("sidebar-parent-manage").click()
        page.get_by_test_id("sidebar-child-users").click()

        with page.expect_download() as download_info:
            page.get_by_role("button", name="Export Users").click()
            time.sleep(5)

        download = download_info.value
        save_path = Path("temp_users_file.xlsx")
        download.save_as(save_path)
        print("Downloaded:", save_path)
        page.get_by_role("button", name="Import Users").click()
        page.locator("input[type='file']").set_input_files(save_path)
        time.sleep(1)
        page.get_by_role("button", name="Upload & Import").click()
        time.sleep(5)
        print("Uploaded same file successfully")
        def wait_for_message(page, text, timeout=10000):
            msg = page.get_by_text(text)
            msg.wait_for(state="visible", timeout=timeout)
            return msg

        wait_for_message(page,"File uploaded! The users are being imported and welcome emails will be sent in the background.")
        print("success message has appeared")
