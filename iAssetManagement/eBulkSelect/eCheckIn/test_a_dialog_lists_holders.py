from playwright.sync_api import sync_playwright, expect
from utils.asset_helper import (
    open_browser, unique_prefix, create_assets, delete_assets, open_assets, asset_row, row_tag, select_all,
    bulk_check_out, open_bulk, date_inputs, EMPLOYEE,
)


def test_dialog_lists_holders():
    """BS-025: the Check In dialog lists each selected asset with who it's coming back from, and
    the status / location pickers default to "Leave unchanged"."""
    with sync_playwright() as p:
        browser, page = open_browser(p)
        prefix = unique_prefix()
        try:
            names = create_assets(page, prefix)
            bulk_check_out(page, prefix, 2)
            open_assets(page, search=prefix)
            tags = {name: row_tag(asset_row(page, name)) for name in names}
            select_all(page, 2)

            dialog = open_bulk(page, "Check In", 2)
            expect(dialog).to_contain_text("Returning these assets from their current holders:")
            for name, tag in tags.items():
                expect(dialog).to_contain_text(f"{tag} ({name}) from {EMPLOYEE}")
            expect(date_inputs(dialog)).to_have_count(1)
            expect(dialog.get_by_placeholder("Leave unchanged")).to_have_count(2)
            for label in ["Return Date", "Set Status", "Return To Location", "Return Notes"]:
                expect(dialog).to_contain_text(label, ignore_case=True)
        finally:
            delete_assets(page, prefix)

        browser.close()
