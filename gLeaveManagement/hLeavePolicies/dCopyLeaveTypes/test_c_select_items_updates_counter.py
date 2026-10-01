from playwright.sync_api import sync_playwright, expect
from utils.leave_policy_helper import (
    open_browser, open_leave_policies, open_create_form, copy_items, copy_counter, copy_note,
)


def test_select_items_updates_counter():
    """LP-027: ticking items updates the 'will be copied' note and the 'N / M selected' counter.

    Known bug: the counter ignores most ticked items (e.g. ticking the first leave
    type leaves it at '0 / 8 selected'), while the note is correct. This test
    fails on the counter until that's fixed.
    """
    with sync_playwright() as p:
        browser, page = open_browser(p)
        open_leave_policies(page)

        form = open_create_form(page)
        leave_types = copy_items(form, "Copy Leave Type")
        work_modes = copy_items(form, "Copy Work Mode")
        total_lt, total_wm = leave_types.count(), work_modes.count()
        assert total_lt >= 2 and total_wm >= 1, "the default source policy needs 2 leave types and 1 work mode"
        shown, expected = [], []

        expect(copy_note(form, "Copy Leave Type")).to_be_hidden()
        leave_types.nth(0).locator("input").check()
        expect(copy_note(form, "Copy Leave Type")).to_have_text("1 leave type will be copied to this policy.")
        shown.append(copy_counter(form, "Copy Leave Type").inner_text().strip())
        expected.append(f"1 / {total_lt} selected")

        leave_types.nth(1).locator("input").check()
        expect(copy_note(form, "Copy Leave Type")).to_have_text("2 leave types will be copied to this policy.")
        shown.append(copy_counter(form, "Copy Leave Type").inner_text().strip())
        expected.append(f"2 / {total_lt} selected")

        work_modes.nth(0).locator("input").check()
        expect(copy_note(form, "Copy Work Mode")).to_have_text("1 work mode will be copied to this policy.")
        shown.append(copy_counter(form, "Copy Work Mode").inner_text().strip())
        expected.append(f"1 / {total_wm} selected")

        leave_types.nth(1).locator("input").uncheck()
        expect(copy_note(form, "Copy Leave Type")).to_have_text("1 leave type will be copied to this policy.")

        assert shown == expected, f"selection counter is wrong: shown {shown}, expected {expected}"

        browser.close()
