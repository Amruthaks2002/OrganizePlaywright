from playwright.sync_api import sync_playwright, expect
from utils.asset_helper import (
    open_browser, unique_prefix, create_assets, delete_assets, open_assets, asset_rows, asset_row, row_id,
    select_all, open_bulk, expect_toast, asset_url, main_content, dock, EMPTY_LIST,
)


def test_bulk_delete():
    """BS-012: confirming Delete removes every selected asset: success toast, the rows are gone
    (also with Include archived on) and their detail pages return 404."""
    with sync_playwright() as p:
        browser, page = open_browser(p)
        prefix = unique_prefix()
        try:
            names = create_assets(page, prefix)
            open_assets(page, search=prefix)
            ids = [row_id(asset_row(page, name)) for name in names]
            select_all(page, 2)

            dialog = open_bulk(page, "Delete", 2)
            dialog.get_by_role("button", name="Delete", exact=True).click()
            expect_toast(page, "2 assets deleted.")
            expect(dialog).to_be_hidden()
            expect(dock(page)).to_be_hidden()
            expect(main_content(page).get_by_text(EMPTY_LIST)).to_be_visible()

            open_assets(page, search=prefix, archived=True)
            expect(asset_rows(page)).to_have_count(0)
            for asset_id in ids:
                assert page.goto(asset_url(asset_id)).status == 404, f"asset {asset_id} still opens"
        finally:
            delete_assets(page, prefix)

        browser.close()
