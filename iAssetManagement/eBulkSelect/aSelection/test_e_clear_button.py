from playwright.sync_api import sync_playwright, expect
from utils.asset_helper import (
    open_browser, unique_prefix, create_assets, delete_assets, open_assets, asset_rows, checked_rows,
    select_all, select_all_box, dock, dock_clear,
)


def test_clear_button():
    """BS-005: Clear unticks every row and the header checkbox and hides the dock, without
    touching the assets."""
    with sync_playwright() as p:
        browser, page = open_browser(p)
        prefix = unique_prefix()
        try:
            create_assets(page, prefix)
            open_assets(page, search=prefix)
            select_all(page, 2)

            dock_clear(page).click()
            expect(checked_rows(page)).to_have_count(0)
            expect(select_all_box(page)).not_to_be_checked()
            expect(dock(page)).to_be_hidden()
            expect(asset_rows(page)).to_have_count(2)
        finally:
            delete_assets(page, prefix)

        browser.close()
