from playwright.sync_api import sync_playwright
from utils.asset_helper import (
    open_browser, unique_prefix, create_assets, delete_assets, open_assets, select_rows, select_all,
    open_bulk, fill_assignment, submit, expect_toast, expect_dock_counts, EMPLOYEE,
)


def test_mixed_selection_counts():
    """BS-006: each dock action counts only the selected assets it applies to - Check In and
    Transfer the assigned ones, Check Out and Delete the unassigned ones - and an action with
    nothing to act on is disabled."""
    with sync_playwright() as p:
        browser, page = open_browser(p)
        prefix = unique_prefix()
        try:
            names = create_assets(page, prefix, 3)
            # check out just the first one
            open_assets(page, search=prefix)
            select_rows(page, names[0])
            dialog = open_bulk(page, "Check Out", 1)
            fill_assignment(page, dialog, EMPLOYEE)
            submit(dialog, "Check Out")
            expect_toast(page, "1 asset checked out.")

            open_assets(page, search=prefix)
            select_all(page, 3)
            expect_dock_counts(page, check_in=1, check_out=2, transfer=1, delete=2)

            open_assets(page, search=prefix)
            select_rows(page, names[1], names[2])
            expect_dock_counts(page, check_in=0, check_out=2, transfer=0, delete=2)
        finally:
            delete_assets(page, prefix)

        browser.close()
