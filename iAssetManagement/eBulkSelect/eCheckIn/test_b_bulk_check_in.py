from playwright.sync_api import sync_playwright, expect
from utils.asset_helper import (
    open_browser, unique_prefix, create_assets, delete_assets, open_assets, asset_row, row_holder, row_status,
    select_all, bulk_check_out, open_bulk, submit, expect_toast, dock,
)


def test_bulk_check_in():
    """BS-026: checking in two assets returns both (Unassigned, Check Out available again), leaves
    their status unchanged and clears the selection."""
    with sync_playwright() as p:
        browser, page = open_browser(p)
        prefix = unique_prefix()
        try:
            names = create_assets(page, prefix)
            bulk_check_out(page, prefix, 2)
            open_assets(page, search=prefix)
            select_all(page, 2)

            dialog = open_bulk(page, "Check In", 2)
            submit(dialog, "Check In")
            expect_toast(page, "2 assets checked in.")
            expect(dialog).to_be_hidden()
            expect(dock(page)).to_be_hidden()

            open_assets(page, search=prefix)
            for name in names:
                row = asset_row(page, name)
                expect(row_holder(row)).to_have_text("Unassigned")
                expect(row_status(row)).to_have_text("Ready to Deploy")
                expect(row.get_by_role("button", name="Check Out")).to_be_visible()
        finally:
            delete_assets(page, prefix)

        browser.close()
