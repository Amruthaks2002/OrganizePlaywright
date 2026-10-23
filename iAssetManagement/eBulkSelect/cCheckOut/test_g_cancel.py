from playwright.sync_api import sync_playwright, expect
from utils.asset_helper import (
    open_browser, unique_prefix, create_assets, delete_assets, open_assets, asset_rows, row_holder, checked_rows,
    select_all, open_bulk, fill_assignment, expect_selected, EMPLOYEE,
)


def test_cancel():
    """BS-020: Cancel in a filled-in Check Out dialog checks nothing out and keeps the selection."""
    with sync_playwright() as p:
        browser, page = open_browser(p)
        prefix = unique_prefix()
        try:
            create_assets(page, prefix)
            open_assets(page, search=prefix)
            select_all(page, 2)

            dialog = open_bulk(page, "Check Out", 2)
            fill_assignment(page, dialog, EMPLOYEE)
            dialog.get_by_role("button", name="Cancel").click()
            expect(dialog).to_be_hidden()
            expect(checked_rows(page)).to_have_count(2)
            expect_selected(page, 2)

            open_assets(page, search=prefix)
            for i in range(2):
                expect(row_holder(asset_rows(page).nth(i))).to_have_text("Unassigned")
        finally:
            delete_assets(page, prefix)

        browser.close()
