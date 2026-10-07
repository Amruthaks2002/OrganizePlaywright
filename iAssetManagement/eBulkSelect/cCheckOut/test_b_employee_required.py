from playwright.sync_api import sync_playwright, expect
from utils.asset_helper import (
    open_browser, unique_prefix, create_assets, delete_assets, open_assets, asset_rows, row_holder, select_all,
    open_bulk, submit,
)


def test_employee_required():
    """BS-015: Check Out without choosing an employee is refused and nothing is checked out."""
    with sync_playwright() as p:
        browser, page = open_browser(p)
        prefix = unique_prefix()
        try:
            create_assets(page, prefix)
            open_assets(page, search=prefix)
            select_all(page, 2)

            dialog = open_bulk(page, "Check Out", 2)
            submit(dialog, "Check Out")
            expect(dialog.get_by_text("Please choose who these assets are going to.")).to_be_visible()
            expect(dialog).to_be_visible()

            dialog.get_by_role("button", name="Cancel").click()
            open_assets(page, search=prefix)
            for i in range(2):
                expect(row_holder(asset_rows(page).nth(i))).to_have_text("Unassigned")
        finally:
            delete_assets(page, prefix)

        browser.close()
