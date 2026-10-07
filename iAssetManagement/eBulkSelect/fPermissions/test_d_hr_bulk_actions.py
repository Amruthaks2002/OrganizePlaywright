from playwright.sync_api import sync_playwright, expect
from utils.asset_helper import (
    open_browser, open_browser_as, unique_prefix, create_assets, delete_assets, open_assets, asset_row,
    row_holder, select_all, open_bulk, fill_assignment, submit, expect_toast, EMPLOYEE,
)


def test_hr_bulk_actions():
    """BS-032: HR gets the full bulk select UI and can bulk check out and check in assets."""
    with sync_playwright() as p:
        browser, page = open_browser(p)
        prefix = unique_prefix()
        try:
            names = create_assets(page, prefix)

            hr_browser, hr_page = open_browser_as(p, "hr")
            open_assets(hr_page, search=prefix)
            select_all(hr_page, 2)
            dialog = open_bulk(hr_page, "Check Out", 2)
            fill_assignment(hr_page, dialog, EMPLOYEE)
            submit(dialog, "Check Out")
            expect_toast(hr_page, "2 assets checked out.")

            open_assets(hr_page, search=prefix)
            for name in names:
                expect(row_holder(asset_row(hr_page, name))).to_have_text(EMPLOYEE)
            select_all(hr_page, 2)
            dialog = open_bulk(hr_page, "Check In", 2)
            submit(dialog, "Check In")
            expect_toast(hr_page, "2 assets checked in.")

            open_assets(hr_page, search=prefix)
            for name in names:
                expect(row_holder(asset_row(hr_page, name))).to_have_text("Unassigned")
            hr_browser.close()
        finally:
            delete_assets(page, prefix)

        browser.close()
