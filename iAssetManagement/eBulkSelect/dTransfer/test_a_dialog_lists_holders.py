from playwright.sync_api import sync_playwright, expect
from utils.asset_helper import (
    open_browser, unique_prefix, create_assets, delete_assets, open_assets, asset_row, row_tag, select_all,
    bulk_check_out, open_bulk, EMPLOYEE,
)


def test_dialog_lists_holders():
    """BS-021: the Transfer dialog lists every selected asset with its current holder and explains
    that the old assignment is closed and a new one opened."""
    with sync_playwright() as p:
        browser, page = open_browser(p)
        prefix = unique_prefix()
        try:
            names = create_assets(page, prefix)
            bulk_check_out(page, prefix, 2)
            open_assets(page, search=prefix)
            tags = [row_tag(asset_row(page, name)) for name in names]
            select_all(page, 2)

            dialog = open_bulk(page, "Transfer", 2)
            expect(dialog).to_contain_text("Transferring these assets to one employee:")
            for tag in tags:
                expect(dialog).to_contain_text(f"{tag} from {EMPLOYEE}")
            expect(dialog).to_contain_text("Each current assignment is closed and a new one opened, so both are kept.")
            for label in ["Transfer To", "Transferred On", "Expected Return", "Notes"]:
                expect(dialog).to_contain_text(label, ignore_case=True)
        finally:
            delete_assets(page, prefix)

        browser.close()
