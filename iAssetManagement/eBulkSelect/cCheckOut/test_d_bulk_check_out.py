from playwright.sync_api import sync_playwright, expect
from utils.asset_helper import (
    open_browser, unique_prefix, create_assets, delete_assets, open_assets, asset_row, row_holder, row_id,
    select_all, open_bulk, fill_assignment, submit, expect_toast, dock, open_asset, assignment_history,
    iso, EMPLOYEE,
)


def test_bulk_check_out():
    """BS-017: checking out two assets to one employee assigns both, clears the selection and
    opens an assignment (with the notes) on each."""
    with sync_playwright() as p:
        browser, page = open_browser(p)
        prefix = unique_prefix()
        notes = f"{prefix} check out"
        try:
            names = create_assets(page, prefix)
            open_assets(page, search=prefix)
            ids = [row_id(asset_row(page, name)) for name in names]
            select_all(page, 2)

            dialog = open_bulk(page, "Check Out", 2)
            fill_assignment(page, dialog, EMPLOYEE, on=iso(0), expected_return=iso(30), notes=notes)
            submit(dialog, "Check Out")
            expect_toast(page, "2 assets checked out.")
            expect(dialog).to_be_hidden()
            expect(dock(page)).to_be_hidden()

            open_assets(page, search=prefix)
            for name in names:
                row = asset_row(page, name)
                expect(row_holder(row)).to_have_text(EMPLOYEE)
                expect(row.get_by_role("button", name="Check In")).to_be_visible()
            for asset_id in ids:
                open_asset(page, asset_id)
                history = assignment_history(page)
                expect(history).to_contain_text(EMPLOYEE)
                expect(history).to_contain_text(notes)
        finally:
            delete_assets(page, prefix)

        browser.close()
