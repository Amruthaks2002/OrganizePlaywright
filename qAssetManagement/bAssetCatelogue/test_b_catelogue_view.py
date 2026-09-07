import time

from playwright.sync_api import sync_playwright
from utils.login_helper import login

def test_catelogue_view():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        login(page)
        page.wait_for_url("**/dashboard**")

        page.get_by_test_id("sidebar-parent-asset management").click()
        time.sleep(1)
        page.get_by_test_id("sidebar-child-asset-catalogue").click()
        time.sleep(2)

        # Search for an existing asset model and verify it is shown
        search_box = page.get_by_placeholder("Search by name…")
        search_box.fill("Latitude")
        time.sleep(1)

        rows = page.locator("table tbody tr")
        assert rows.count() == 1, f"Expected 1 matching asset model, found {rows.count()}"

        row_text = rows.first.inner_text()
        assert "Latitude 5440" in row_text, f"Expected 'Latitude 5440' in row, got: {row_text}"
        print(f"Asset model found: {row_text}")
        time.sleep(3)
