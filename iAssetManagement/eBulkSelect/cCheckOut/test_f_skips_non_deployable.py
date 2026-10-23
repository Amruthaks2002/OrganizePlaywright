from playwright.sync_api import sync_playwright, expect
from utils.asset_helper import (
    open_browser, unique_prefix, create_asset, delete_assets, open_assets, asset_row, row_tag, row_holder,
    select_all, open_bulk, fill_assignment, submit, expect_toast, EMPLOYEE,
)


def test_skips_non_deployable():
    """BS-019: an Under Repair asset in a bulk Check Out is skipped with the reason, and the
    Ready to Deploy one is still checked out."""
    with sync_playwright() as p:
        browser, page = open_browser(p)
        prefix = unique_prefix()
        ready, repair = f"{prefix} ready", f"{prefix} repair"
        try:
            create_asset(page, ready)
            create_asset(page, repair, status="Under Repair")
            open_assets(page, search=prefix)
            repair_tag = row_tag(asset_row(page, repair))
            select_all(page, 2)

            dialog = open_bulk(page, "Check Out", 2)
            fill_assignment(page, dialog, EMPLOYEE)
            submit(dialog, "Check Out")
            expect_toast(page, f"1 asset checked out. Skipped 1: {repair_tag}: "
                               "This asset cannot be assigned while it is set to Under Repair.")

            open_assets(page, search=prefix)
            expect(row_holder(asset_row(page, ready))).to_have_text(EMPLOYEE)
            expect(row_holder(asset_row(page, repair))).to_have_text("Unassigned")
        finally:
            delete_assets(page, prefix)

        browser.close()
