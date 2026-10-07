from playwright.sync_api import sync_playwright, expect
from utils.asset_helper import (
    open_browser, unique_prefix, create_assets, delete_assets, open_assets, asset_row, row_holder, row_id,
    select_all, bulk_check_out, open_bulk, fill_assignment, submit, expect_toast, dock, open_asset,
    assignment_history, EMPLOYEE, TRANSFER_TO,
)


def test_bulk_transfer():
    """BS-023: transferring two assets moves both to the new employee, clears the selection, and
    keeps the old assignment in each asset's history next to the new one."""
    with sync_playwright() as p:
        browser, page = open_browser(p)
        prefix = unique_prefix()
        notes = f"{prefix} transfer"
        try:
            names = create_assets(page, prefix)
            bulk_check_out(page, prefix, 2)
            open_assets(page, search=prefix)
            ids = [row_id(asset_row(page, name)) for name in names]
            select_all(page, 2)

            dialog = open_bulk(page, "Transfer", 2)
            fill_assignment(page, dialog, TRANSFER_TO, notes=notes)
            submit(dialog, "Transfer")
            expect_toast(page, "2 assets transferred.")
            expect(dialog).to_be_hidden()
            expect(dock(page)).to_be_hidden()

            open_assets(page, search=prefix)
            for name in names:
                expect(row_holder(asset_row(page, name))).to_have_text(TRANSFER_TO)
            for asset_id in ids:
                open_asset(page, asset_id)
                history = assignment_history(page)
                expect(history).to_contain_text(TRANSFER_TO)
                expect(history).to_contain_text(EMPLOYEE)
                expect(history).to_contain_text(notes)
        finally:
            delete_assets(page, prefix)

        browser.close()
