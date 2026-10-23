from playwright.sync_api import sync_playwright, expect
from utils.asset_helper import (
    open_browser, unique_prefix, create_assets, delete_assets, open_assets, asset_row, row_checkbox, dock,
    expect_selected, expect_dock_counts,
)


def test_select_one_row():
    """BS-001: ticking one unassigned asset shows the dock with "1 asset selected", Check Out and
    Delete at 1, and Check In / Transfer disabled at 0."""
    with sync_playwright() as p:
        browser, page = open_browser(p)
        prefix = unique_prefix()
        try:
            names = create_assets(page, prefix)
            open_assets(page, search=prefix)
            expect(dock(page)).to_be_hidden()

            row_checkbox(asset_row(page, names[0])).check()
            expect_selected(page, 1)
            expect_dock_counts(page, check_in=0, check_out=1, transfer=0, delete=1)
        finally:
            delete_assets(page, prefix)

        browser.close()
