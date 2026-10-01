from playwright.sync_api import sync_playwright, expect
from utils.leave_policy_helper import (
    open_browser, open_leave_policies, existing_policy_names, select_policy, item_names,
    open_create_form, copy_source, copy_items, copy_item_names,
)


def test_change_copy_source():
    """LP-026: changing the source policy reloads the lists with that policy's leave types and work modes."""
    with sync_playwright() as p:
        browser, page = open_browser(p)
        open_leave_policies(page)

        expected = {}
        for name in existing_policy_names(page):
            select_policy(page, name)
            expected[name] = {"Copy Leave Type": item_names(page, "Leave Types"),
                              "Copy Work Mode": item_names(page, "Work Modes")}

        form = open_create_form(page)
        for name, columns in expected.items():
            for column, items in columns.items():
                copy_source(form, column).select_option(label=name)
                expect(copy_items(form, column)).to_have_count(len(items))
                assert sorted(copy_item_names(form, column)) == sorted(items), f"{name} / {column}"

        browser.close()
