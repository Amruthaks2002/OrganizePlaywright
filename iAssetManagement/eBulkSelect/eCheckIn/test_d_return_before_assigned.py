from playwright.sync_api import sync_playwright, expect
from utils.asset_helper import (
    open_browser, unique_prefix, create_assets, delete_assets, open_assets, asset_row, row_tag, row_holder,
    select_all, bulk_check_out, open_bulk, fill_check_in, submit, expect_toast, iso, EMPLOYEE,
)


def test_return_before_assigned():
    """BS-028: a return date before the assets were assigned checks nothing in and reports each
    asset with the reason."""
    with sync_playwright() as p:
        browser, page = open_browser(p)
        prefix = unique_prefix()
        try:
            names = create_assets(page, prefix)
            bulk_check_out(page, prefix, 2)
            open_assets(page, search=prefix)
            tags = [row_tag(asset_row(page, name)) for name in names]
            select_all(page, 2)

            dialog = open_bulk(page, "Check In", 2)
            fill_check_in(page, dialog, returned_on=iso(-3))
            submit(dialog, "Check In")
            expect_toast(page, "No assets were checked in.")
            for tag in tags:
                expect_toast(page, f"{tag}: The return date cannot be before the asset was assigned.")

            open_assets(page, search=prefix)
            for name in names:
                expect(row_holder(asset_row(page, name))).to_have_text(EMPLOYEE)
        finally:
            delete_assets(page, prefix)

        browser.close()
