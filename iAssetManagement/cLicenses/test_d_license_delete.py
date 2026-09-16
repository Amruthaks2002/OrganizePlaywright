import re
import time

from playwright.sync_api import sync_playwright
from utils.login_helper import login

def wait_for_message(page, pattern, timeout=10000):
    msg = page.get_by_text(pattern)
    msg.wait_for(state="visible", timeout=timeout)
    return msg

def test_license_catelogue_delete():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        page.set_default_timeout(45000)
        login(page)
        page.wait_for_url("**/dashboard**")

        page.get_by_test_id("sidebar-parent-asset management").click()
        time.sleep(1)
        page.get_by_test_id("sidebar-child-licences").click()
        time.sleep(2)

        # Delete the license created/edited by the earlier license tests
        search_box = page.get_by_placeholder("Search name, publisher, licensee…")
        search_box.fill("Automation License")
        time.sleep(1.5)

        row = page.locator("table tbody tr").first
        row_text = row.inner_text()
        assert "Automation License" in row_text, f"Expected 'Automation License' in row, got: {row_text}"

        row.get_by_role("link", name="View").click()
        page.wait_for_url(re.compile(r".*/licenses/\d+$"))
        time.sleep(1)

        # A license with an assigned seat can't be deleted directly, so release it first
        release_buttons = page.get_by_role("button", name="Release")
        for _ in range(release_buttons.count()):
            page.get_by_role("button", name="Release").first.click()
            time.sleep(1)
            confirm = page.get_by_role("button", name=re.compile("^release$", re.I)).last
            if confirm.is_visible():
                confirm.click()
                time.sleep(1)

        # Delete straight from the license view page
        page.get_by_role("button", name="Delete", exact=True).click()
        time.sleep(1)

        page.get_by_role("button", name="Delete", exact=True).last.click()
        wait_for_message(page, re.compile("Licence deleted successfully", re.I))
        print("Licence deleted successfully.")
        time.sleep(2)
