from playwright.sync_api import sync_playwright, expect
from utils.asset_helper import (
    open_browser, unique_prefix, create_assets, delete_assets, open_assets, asset_row, row_tag, select_all,
    open_bulk, date_inputs,
)


def test_dialog_lists_assets():
    """BS-014: the Check Out dialog lists every selected asset by tag and name, with an empty
    Assign To picker, both dates and Notes."""
    with sync_playwright() as p:
        browser, page = open_browser(p)
        prefix = unique_prefix()
        try:
            names = create_assets(page, prefix)
            open_assets(page, search=prefix)
            tags = {name: row_tag(asset_row(page, name)) for name in names}
            select_all(page, 2)

            dialog = open_bulk(page, "Check Out", 2)
            expect(dialog).to_contain_text("Checking out these assets to one employee:")
            for name, tag in tags.items():
                expect(dialog).to_contain_text(f"{tag} ({name})")
            expect(dialog.get_by_placeholder("Search for an employee…")).to_have_value("")
            expect(date_inputs(dialog)).to_have_count(2)
            for label in ["Assign To", "Assigned On", "Expected Return", "Notes"]:
                expect(dialog).to_contain_text(label, ignore_case=True)
        finally:
            delete_assets(page, prefix)

        browser.close()
