from datetime import date, timedelta

from playwright.sync_api import sync_playwright, expect
from utils.asset_helper import (
    open_browser, unique_prefix, create_assets, delete_assets, open_assets, asset_row, row_holder, row_id,
    select_all, open_bulk, fill_assignment, submit, expect_toast, open_asset, assignment_history, iso, EMPLOYEE,
)


def test_future_assigned_date():
    """BS-034: an Assigned On date in the future is accepted (by design) and kept on the assignment.

    Such an asset can only be checked in on or after that date, so the cleanup checks it in with a
    later return date."""
    with sync_playwright() as p:
        browser, page = open_browser(p)
        prefix = unique_prefix()
        future = date.today() + timedelta(days=60)
        try:
            names = create_assets(page, prefix)
            open_assets(page, search=prefix)
            asset_id = row_id(asset_row(page, names[0]))
            select_all(page, 2)

            dialog = open_bulk(page, "Check Out", 2)
            fill_assignment(page, dialog, EMPLOYEE, on=iso(60))
            submit(dialog, "Check Out")
            expect_toast(page, "2 assets checked out.")

            open_assets(page, search=prefix)
            for name in names:
                expect(row_holder(asset_row(page, name))).to_have_text(EMPLOYEE)
            open_asset(page, asset_id)
            expect(assignment_history(page)).to_contain_text(f"{future:%b} {future.day}, {future.year}")
        finally:
            delete_assets(page, prefix)

        browser.close()
