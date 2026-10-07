from playwright.sync_api import sync_playwright, expect
from utils.asset_helper import (
    open_browser, unique_prefix, create_assets, delete_assets, open_assets, asset_rows, row_holder, select_all,
    open_bulk, fill_assignment, submit, expect_toast, iso, EMPLOYEE,
)

ERROR = "The expected return date cannot be before the assignment date."


def test_return_before_assigned():
    """BS-016: an expected return date before the assigned-on date is refused, the dialog stays
    open with the error, and nothing is checked out."""
    with sync_playwright() as p:
        browser, page = open_browser(p)
        prefix = unique_prefix()
        try:
            create_assets(page, prefix)
            open_assets(page, search=prefix)
            select_all(page, 2)

            dialog = open_bulk(page, "Check Out", 2)
            fill_assignment(page, dialog, EMPLOYEE, on=iso(0), expected_return=iso(-3))
            with page.expect_response("**/assets/bulk/check-out"):
                submit(dialog, "Check Out")
            expect_toast(page, ERROR)
            expect(dialog.get_by_text(ERROR)).to_be_visible()
            expect(dialog).to_be_visible()

            dialog.get_by_role("button", name="Cancel").click()
            open_assets(page, search=prefix)
            for i in range(2):
                expect(row_holder(asset_rows(page).nth(i))).to_have_text("Unassigned")
        finally:
            delete_assets(page, prefix)

        browser.close()
