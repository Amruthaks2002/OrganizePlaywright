from playwright.sync_api import sync_playwright, expect
from utils.leave_policy_helper import (
    open_browser, open_leave_policies, unique_policy_name, create_policy, delete_policy,
    open_edit_form, copy_source, existing_policy_names, is_test_policy,
)


def test_edit_copy_source_excludes_current():
    """LP-033: in the Edit form the copy-source dropdowns leave out the policy being edited."""
    with sync_playwright() as p:
        browser, page = open_browser(p)
        open_leave_policies(page)
        name = unique_policy_name()
        try:
            create_policy(page, name)
            others = existing_policy_names(page)

            form = open_edit_form(page, name)
            for column in ["Copy Leave Type", "Copy Work Mode"]:
                options = copy_source(form, column).evaluate("e => [...e.options].map(o => o.text.trim())")
                assert name not in options, column
                assert sorted(o for o in options if not is_test_policy(o)) == sorted(others), column
            form.get_by_role("button", name="Cancel").click()
            expect(form).to_be_hidden()
        finally:
            delete_policy(page, name)

        browser.close()
