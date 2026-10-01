from playwright.sync_api import sync_playwright, expect
from utils.leave_policy_helper import (
    open_browser, open_leave_policies, unique_policy_name, create_policy, delete_policy,
    open_edit_form, set_active, expect_toast, policy_card, card_status, detail_badges, goto, POLICIES_URL,
)


def test_toggle_active_status():
    """LP-036: switching Active off and back on updates the status badge each time."""
    with sync_playwright() as p:
        browser, page = open_browser(p)
        open_leave_policies(page)
        name = unique_policy_name()
        try:
            create_policy(page, name)

            for active, label in [(False, "Inactive"), (True, "Active")]:
                form = open_edit_form(page, name)
                set_active(form, active)
                form.get_by_role("button", name="Update Policy").click()
                expect_toast(page, "Leave policy updated successfully.")
                expect(form).to_be_hidden()
                expect(card_status(policy_card(page, name))).to_have_text(label)
                expect(detail_badges(page).first).to_have_text(label)
                goto(page, POLICIES_URL)
        finally:
            delete_policy(page, name)

        browser.close()
