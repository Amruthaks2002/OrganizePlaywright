from playwright.sync_api import sync_playwright, expect
from utils.asset_helper import (
    open_browser, unique_prefix, create_assets, delete_assets, open_assets, asset_rows, select_all, bulk_check_out,
    dock_button, expect_dock_counts,
)


def test_assigned_not_deletable():
    """BS-013: checked-out assets don't count towards Delete - with only assigned assets selected,
    Delete (0) is disabled and nothing can be deleted."""
    with sync_playwright() as p:
        browser, page = open_browser(p)
        prefix = unique_prefix()
        try:
            create_assets(page, prefix)
            bulk_check_out(page, prefix, 2)

            open_assets(page, search=prefix)
            select_all(page, 2)
            expect_dock_counts(page, check_in=2, check_out=0, transfer=2, delete=0)
            dock_button(page, "Delete", 0).click(force=True)
            open_assets(page, search=prefix)
            expect(asset_rows(page)).to_have_count(2)
        finally:
            delete_assets(page, prefix)

        browser.close()
