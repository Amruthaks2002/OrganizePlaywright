from playwright.sync_api import sync_playwright, expect
from utils.asset_helper import (
    open_browser, unique_prefix, create_assets, delete_assets, open_assets, select_all, open_bulk,
)


def test_confirm_dialog():
    """BS-010: Delete (2) asks for confirmation, naming how many assets and that they can be restored."""
    with sync_playwright() as p:
        browser, page = open_browser(p)
        prefix = unique_prefix()
        try:
            create_assets(page, prefix)
            open_assets(page, search=prefix)
            select_all(page, 2)

            dialog = open_bulk(page, "Delete", 2)
            expect(dialog).to_contain_text("Delete Assets")
            expect(dialog).to_contain_text("Delete 2 assets? They can be restored by an administrator.")
            expect(dialog.get_by_role("button", name="Keep")).to_be_visible()
            expect(dialog.get_by_role("button", name="Delete", exact=True)).to_be_visible()
        finally:
            delete_assets(page, prefix)

        browser.close()
