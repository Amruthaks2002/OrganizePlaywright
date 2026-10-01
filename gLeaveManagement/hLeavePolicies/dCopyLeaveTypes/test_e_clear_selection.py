from playwright.sync_api import sync_playwright, expect
from utils.leave_policy_helper import (
    open_browser, open_leave_policies, open_create_form, copy_column, copy_items, copy_counter, copy_note,
)


def test_clear_selection():
    """LP-029: Clear unticks every item and resets the counter to 0."""
    with sync_playwright() as p:
        browser, page = open_browser(p)
        open_leave_policies(page)

        form = open_create_form(page)
        for column in ["Copy Leave Type", "Copy Work Mode"]:
            items = copy_items(form, column)
            total = items.count()
            for item in items.all():
                item.locator("input").check()
            expect(copy_note(form, column)).to_be_visible()

            copy_column(form, column).get_by_role("button", name="Clear").click()
            for item in items.all():
                expect(item.locator("input")).not_to_be_checked()
            expect(copy_counter(form, column)).to_have_text(f"0 / {total} selected")
            expect(copy_note(form, column)).to_be_hidden()

        browser.close()
