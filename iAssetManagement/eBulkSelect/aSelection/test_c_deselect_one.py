from playwright.sync_api import sync_playwright, expect
from utils.asset_helper import (
    open_browser, unique_prefix, create_assets, delete_assets, open_assets, asset_row, row_checkbox,
    checked_rows, select_all, select_all_box, expect_selected, expect_dock_counts,
)


def test_deselect_one():
    """BS-003: unticking one row after Select all lowers the count and unticks the header checkbox."""
    with sync_playwright() as p:
        browser, page = open_browser(p)
        prefix = unique_prefix()
        try:
            names = create_assets(page, prefix, 3)
            open_assets(page, search=prefix)
            select_all(page, 3)

            row_checkbox(asset_row(page, names[0])).uncheck()
            expect(checked_rows(page)).to_have_count(2)
            expect(select_all_box(page)).not_to_be_checked()
            expect_selected(page, 2)
            expect_dock_counts(page, check_in=0, check_out=2, transfer=0, delete=2)

            # ticking it again brings the header back
            row_checkbox(asset_row(page, names[0])).check()
            expect(select_all_box(page)).to_be_checked()
            expect_selected(page, 3)
        finally:
            delete_assets(page, prefix)

        browser.close()
