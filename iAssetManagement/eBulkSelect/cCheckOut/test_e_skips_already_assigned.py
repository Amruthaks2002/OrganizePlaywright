from playwright.sync_api import sync_playwright, expect
from utils.asset_helper import (
    open_browser, unique_prefix, create_assets, delete_assets, open_assets, asset_row, row_tag, row_holder,
    select_all, open_bulk, fill_assignment, submit, expect_toast, single_check_out, EMPLOYEE,
)


def test_skips_already_assigned():
    """BS-018: if one of the selected assets is checked out in another tab before the bulk Check Out
    is submitted, the others still go through and that one is reported as skipped."""
    with sync_playwright() as p:
        browser, page = open_browser(p)
        prefix = unique_prefix()
        try:
            names = create_assets(page, prefix)
            open_assets(page, search=prefix)
            stale_tag = row_tag(asset_row(page, names[0]))
            select_all(page, 2)

            other = page.context.new_page()
            single_check_out(other, prefix, names[0])
            other.close()

            dialog = open_bulk(page, "Check Out", 2)
            fill_assignment(page, dialog, EMPLOYEE)
            submit(dialog, "Check Out")
            expect_toast(page, f"1 asset checked out. Skipped 1: {stale_tag}: "
                               f"This asset is already assigned to {EMPLOYEE}.")

            open_assets(page, search=prefix)
            for name in names:
                expect(row_holder(asset_row(page, name))).to_have_text(EMPLOYEE)
        finally:
            delete_assets(page, prefix)

        browser.close()
