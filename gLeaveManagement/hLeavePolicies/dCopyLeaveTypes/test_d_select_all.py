from playwright.sync_api import sync_playwright, expect
from utils.leave_policy_helper import (
    open_browser, open_leave_policies, open_create_form, copy_column, copy_items, copy_counter, copy_note,
)


def test_select_all():
    """LP-028: Select All ticks every item and the counter shows M / M.

    Known bug: the boxes all tick and the note is right, but the counter shows
    e.g. '2 / 8 selected' and '1 / 2 selected'. This test fails until it's fixed.
    """
    with sync_playwright() as p:
        browser, page = open_browser(p)
        open_leave_policies(page)

        form = open_create_form(page)
        counters = {}
        for column, noun in [("Copy Leave Type", "leave types"), ("Copy Work Mode", "work modes")]:
            items = copy_items(form, column)
            total = items.count()
            copy_column(form, column).get_by_role("button", name="Select All").click()

            for item in items.all():
                expect(item.locator("input")).to_be_checked()
            expect(copy_note(form, column)).to_have_text(f"{total} {noun} will be copied to this policy.")
            counters[column] = (copy_counter(form, column).inner_text().strip(), f"{total} / {total} selected")

        actual = {column: shown for column, (shown, _) in counters.items()}
        expected = {column: wanted for column, (_, wanted) in counters.items()}
        assert actual == expected, f"Select All counter is wrong: shown {actual}, expected {expected}"

        browser.close()
