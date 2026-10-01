from playwright.sync_api import sync_playwright, expect
from utils.leave_policy_helper import (
    open_browser, open_leave_policies, unique_policy_name, create_policy, delete_policy,
    open_edit_form, fill_policy_form, dialog, close_x, goto, POLICIES_URL, select_policy,
    detail_badges, detail_description,
)


def test_cancel_edit_discards_changes():
    """LP-039: closing the Edit form with Cancel or X throws away the changes."""
    with sync_playwright() as p:
        browser, page = open_browser(p)
        open_leave_policies(page)
        name = unique_policy_name()
        try:
            create_policy(page, name, region="QA Region", description="Original description")

            for close in ["Cancel", "X"]:
                form = open_edit_form(page, name)
                fill_policy_form(form, region="Changed Region", description="Changed description")
                if close == "Cancel":
                    form.get_by_role("button", name="Cancel").click()
                else:
                    close_x(dialog(page, "Edit Leave Policy")).click()
                expect(form).to_be_hidden()

                goto(page, POLICIES_URL)
                select_policy(page, name)
                expect(detail_badges(page)).to_have_text(["Active", "QA Region"])
                expect(detail_description(page)).to_have_text("Original description")
        finally:
            delete_policy(page, name)

        browser.close()
