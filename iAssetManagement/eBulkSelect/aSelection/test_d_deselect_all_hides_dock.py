from playwright.sync_api import sync_playwright, expect
from utils.asset_helper import (
    open_browser, unique_prefix, create_assets, delete_assets, open_assets, asset_row, row_checkbox,
    checked_rows, select_all, select_all_box, dock,
)


def test_deselect_all_hides_dock():
    """BS-004: unticking every row (one by one, or with the header checkbox) hides the dock."""
    with sync_playwright() as p:
        browser, page = open_browser(p)
        prefix = unique_prefix()
        try:
            names = create_assets(page, prefix)
            open_assets(page, search=prefix)

            select_all(page, 2)
            for name in names:
                row_checkbox(asset_row(page, name)).uncheck()
            expect(checked_rows(page)).to_have_count(0)
            expect(dock(page)).to_be_hidden()

            select_all(page, 2)
            select_all_box(page).uncheck()
            expect(checked_rows(page)).to_have_count(0)
            expect(dock(page)).to_be_hidden()
        finally:
            delete_assets(page, prefix)

        browser.close()
