from playwright.sync_api import sync_playwright, expect
from utils.leave_policy_helper import (
    open_browser, open_leave_policies, unique_policy_name, create_policy, delete_policy,
    open_edit_form, name_input, region_input, description_input, active_toggle, checked_weekends,
)


def test_edit_form_prefilled():
    """LP-032: the Edit form opens with the policy's saved values."""
    with sync_playwright() as p:
        browser, page = open_browser(p)
        open_leave_policies(page)
        name = unique_policy_name()
        try:
            create_policy(page, name, region="QA Region", description="QA automation policy",
                          active=False, weekends=["Friday", "Saturday"])

            form = open_edit_form(page, name)
            expect(name_input(form)).to_have_value(name)
            expect(region_input(form)).to_have_value("QA Region")
            expect(description_input(form)).to_have_value("QA automation policy")
            expect(active_toggle(form)).not_to_be_checked()
            assert checked_weekends(form) == ["Friday", "Saturday"]
            expect(form.get_by_role("button", name="Update Policy")).to_be_visible()
            expect(form.get_by_role("button", name="Delete Policy")).to_be_visible()
            form.get_by_role("button", name="Cancel").click()
            expect(form).to_be_hidden()
        finally:
            delete_policy(page, name)

        browser.close()
