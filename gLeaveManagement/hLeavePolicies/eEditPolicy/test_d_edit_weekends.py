from playwright.sync_api import sync_playwright, expect
from utils.leave_policy_helper import (
    open_browser, open_leave_policies, unique_policy_name, create_policy, delete_policy,
    open_edit_form, set_weekends, checked_weekends, expect_toast, goto, POLICIES_URL,
)


def test_edit_weekends():
    """LP-035: changed weekend days are saved and shown when the form is reopened."""
    with sync_playwright() as p:
        browser, page = open_browser(p)
        open_leave_policies(page)
        name = unique_policy_name()
        try:
            create_policy(page, name, weekends=["Saturday", "Sunday"])

            form = open_edit_form(page, name)
            set_weekends(form, ["Friday"])
            form.get_by_role("button", name="Update Policy").click()
            expect_toast(page, "Leave policy updated successfully.")
            expect(form).to_be_hidden()

            goto(page, POLICIES_URL)
            form = open_edit_form(page, name)
            assert checked_weekends(form) == ["Friday"]
            form.get_by_role("button", name="Cancel").click()
            expect(form).to_be_hidden()
        finally:
            delete_policy(page, name)

        browser.close()
