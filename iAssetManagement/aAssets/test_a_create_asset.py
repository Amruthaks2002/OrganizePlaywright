import time

from playwright.sync_api import sync_playwright
from utils.login_helper import login

def wait_for_message(page, text, timeout=10000):
    msg = page.get_by_text(text)
    msg.wait_for(state="visible", timeout=timeout)
    return msg


def select_option(page, container_id, option_text):
    page.locator(f"#{container_id}").click()
    time.sleep(0.5)
    page.locator("li[role=option]", has_text=option_text).first.click()
    time.sleep(0.3)

def test_create_asset():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        login(page)
        page.wait_for_url("**/dashboard**")

        page.get_by_test_id("sidebar-parent-asset management").click()
        time.sleep(1)
        page.get_by_test_id("sidebar-child-assets").click()

        page.get_by_role("link", name="New Asset").click()
        time.sleep(3)

        unique_suffix = str(int(time.time()))

        # Identification (Asset Tag is auto-generated, left untouched)
        page.locator("#serial").fill(f"SN-TEST-{unique_suffix}")
        page.locator("#name").fill("Automation Test Asset")

        # Classification
        select_option(page, "asset_model_id", "Latitude 5440")
        select_option(page, "asset_status_id", "Ready to Deploy")
        select_option(page, "asset_location_id", "Calicut")
        select_option(page, "asset_supplier_id", "Dell Technologies")

        # Purchase
        page.locator("#purchase_date").fill("2025-01-15")
        page.locator("#purchase_cost").fill("50000")

        # Invoice
        page.locator("#invoice_number").fill(f"INV-{unique_suffix}")
        page.locator("#invoice_date").fill("2025-01-16")
        page.locator("#invoice_amount").fill("50000")

        # Warranty
        page.locator("#warranty_start_date").fill("2025-01-15")
        page.locator("#warranty_end_date").fill("2027-01-15")
        page.locator("#warranty_provider").fill("Dell Warranty")
        page.locator("#warranty_reference_number").fill("WREF-1001")

        # Notes
        page.locator("#notes").fill("Created by automation test.")

        page.get_by_role("button", name="Create Asset").click()
        wait_for_message(page, "Asset created successfully.")
        print("Asset created successfully.")
        time.sleep(3)