from playwright.sync_api import sync_playwright, expect
from utils.asset_helper import (
    open_browser, unique_prefix, create_assets, delete_assets, open_assets, asset_rows, checked_rows, select_all,
    open_bulk, expect_selected,
)


def test_keep():
    """BS-011: Keep closes the delete confirmation, deletes nothing and leaves the selection as it was."""
    with sync_playwright() as p:
        browser, page = open_browser(p)
        prefix = unique_prefix()
        try:
            create_assets(page, prefix)
            open_assets(page, search=prefix)
            select_all(page, 2)

            dialog = open_bulk(page, "Delete", 2)
            dialog.get_by_role("button", name="Keep").click()
            expect(dialog).to_be_hidden()
            expect(checked_rows(page)).to_have_count(2)
            expect_selected(page, 2)

            open_assets(page, search=prefix)
            expect(asset_rows(page)).to_have_count(2)
        finally:
            delete_assets(page, prefix)

        browser.close()
