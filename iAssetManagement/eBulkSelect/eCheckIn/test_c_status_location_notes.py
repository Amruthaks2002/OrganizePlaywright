import re

from playwright.sync_api import sync_playwright, expect
from utils.asset_helper import (
    open_browser, unique_prefix, create_assets, delete_assets, open_assets, asset_row, row_holder, row_status,
    row_id, select_all, bulk_check_out, open_bulk, fill_check_in, submit, expect_toast, open_asset,
    assignment_history, main_content, LOCATION,
)


def test_status_location_notes():
    """BS-027: Check In with a status, a location and notes applies them to every returned asset."""
    with sync_playwright() as p:
        browser, page = open_browser(p)
        prefix = unique_prefix()
        notes = f"{prefix} return"
        try:
            names = create_assets(page, prefix)
            bulk_check_out(page, prefix, 2)
            open_assets(page, search=prefix)
            ids = [row_id(asset_row(page, name)) for name in names]
            select_all(page, 2)

            dialog = open_bulk(page, "Check In", 2)
            fill_check_in(page, dialog, status="Under Repair", location=LOCATION, notes=notes)
            submit(dialog, "Check In")
            expect_toast(page, "2 assets checked in.")

            open_assets(page, search=prefix)
            for name in names:
                row = asset_row(page, name)
                expect(row_holder(row)).to_have_text("Unassigned")
                expect(row_status(row)).to_have_text("Under Repair")
            for asset_id in ids:
                open_asset(page, asset_id)
                expect(main_content(page)).to_contain_text(re.compile(rf"LOCATION\s*{LOCATION}", re.I))
                expect(assignment_history(page)).to_contain_text(notes)
        finally:
            delete_assets(page, prefix)

        browser.close()
