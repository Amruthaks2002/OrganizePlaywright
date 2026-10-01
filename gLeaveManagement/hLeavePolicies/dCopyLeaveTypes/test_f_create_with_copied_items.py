from playwright.sync_api import sync_playwright, expect
from utils.leave_policy_helper import (
    open_browser, open_leave_policies, unique_policy_name, open_create_form, fill_policy_form,
    copy_item_names, expect_toast, policy_card, select_policy, item_names, items_count,
    delete_policy, policy_names,
)


def test_create_with_copied_items():
    """LP-030: a policy created with copied leave types and work modes has exactly those items."""
    with sync_playwright() as p:
        browser, page = open_browser(p)
        open_leave_policies(page)
        name = unique_policy_name()
        source = policy_names(page)[0]
        try:
            form = open_create_form(page)
            fill_policy_form(form, name=name, copy_from=source)
            leave_types = copy_item_names(form, "Copy Leave Type")[:2]
            work_modes = copy_item_names(form, "Copy Work Mode")[:1]
            fill_policy_form(form, leave_types=leave_types, work_modes=work_modes)
            form.get_by_role("button", name="Create Policy").click()
            expect_toast(page, "Leave policy created successfully.")
            expect(policy_card(page, name)).to_have_count(1)

            select_policy(page, name)
            assert sorted(item_names(page, "Leave Types")) == sorted(leave_types)
            assert sorted(item_names(page, "Work Modes")) == sorted(work_modes)
            assert items_count(page, "Leave Types") == len(leave_types)
            assert items_count(page, "Work Modes") == len(work_modes)
        finally:
            delete_policy(page, name)

        browser.close()
