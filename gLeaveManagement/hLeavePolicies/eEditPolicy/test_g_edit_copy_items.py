from playwright.sync_api import sync_playwright, expect
from utils.leave_policy_helper import (
    open_browser, open_leave_policies, unique_policy_name, create_policy, delete_policy,
    existing_policy_names, open_edit_form, fill_policy_form, copy_item_names, expect_toast,
    select_policy, item_names, items_count,
)


def test_edit_copy_items():
    """LP-038: leave types and work modes copied in the Edit form are added to the policy."""
    with sync_playwright() as p:
        browser, page = open_browser(p)
        open_leave_policies(page)
        name = unique_policy_name()
        source = existing_policy_names(page)[0]
        try:
            create_policy(page, name)

            form = open_edit_form(page, name)
            fill_policy_form(form, copy_from=source)
            leave_types = copy_item_names(form, "Copy Leave Type")[:1]
            work_modes = copy_item_names(form, "Copy Work Mode")[:1]
            fill_policy_form(form, leave_types=leave_types, work_modes=work_modes)
            form.get_by_role("button", name="Update Policy").click()
            expect_toast(page, "Leave policy updated successfully.")
            expect(form).to_be_hidden()

            select_policy(page, name)
            assert item_names(page, "Leave Types") == leave_types
            assert item_names(page, "Work Modes") == work_modes
            assert items_count(page, "Leave Types") == 1
            assert items_count(page, "Work Modes") == 1
        finally:
            delete_policy(page, name)

        browser.close()
