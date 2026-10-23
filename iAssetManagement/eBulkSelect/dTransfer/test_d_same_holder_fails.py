from playwright.sync_api import sync_playwright, expect
from utils.asset_helper import (
    open_browser, unique_prefix, create_assets, delete_assets, open_assets, asset_row, row_tag, row_holder,
    select_all, bulk_check_out, open_bulk, fill_assignment, submit, expect_toast, expect_selected, EMPLOYEE,
)


def test_same_holder_fails():
    """BS-024: transferring assets to the employee who already holds them transfers nothing,
    reports every asset with the reason, and keeps the selection so it can be corrected."""
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
            fill_assignment(page, dialog, EMPLOYEE)
            submit(dialog, "Transfer")
            expect_toast(page, "No assets were transferred.")
            for tag in tags:
                expect_toast(page, f"{tag}: This asset is already assigned to that employee.")
            expect_selected(page, 2)

            open_assets(page, search=prefix)
            for name in names:
                expect(row_holder(asset_row(page, name))).to_have_text(EMPLOYEE)
        finally:
            delete_assets(page, prefix)

        browser.close()
