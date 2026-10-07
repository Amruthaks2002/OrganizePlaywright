from playwright.sync_api import sync_playwright, expect
from utils.asset_helper import (
    open_browser, unique_prefix, create_assets, delete_assets, open_assets, asset_rows, checked_rows,
    select_all_box, expect_selected, expect_dock_counts,
)


def test_select_all():
    """BS-002: the header checkbox ticks every row on the page and the dock counts all of them."""
    with sync_playwright() as p:
        browser, page = open_browser(p)
        prefix = unique_prefix()
        try:
            create_assets(page, prefix, 3)
            open_assets(page, search=prefix)
            expect(asset_rows(page)).to_have_count(3)

            select_all_box(page).check()
            expect(checked_rows(page)).to_have_count(3)
            expect(select_all_box(page)).to_be_checked()
            expect_selected(page, 3)
            expect_dock_counts(page, check_in=0, check_out=3, transfer=0, delete=3)
        finally:
            delete_assets(page, prefix)

        browser.close()
