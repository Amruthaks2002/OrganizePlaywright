from playwright.sync_api import sync_playwright, expect
from utils.leave_policy_helper import (
    open_browser, open_leave_policies, unique_policy_name, create_policy, delete_policy,
    select_policy, detail_header, delete_dialog, expect_toast, policy_card, detail_name,
    goto, POLICIES_URL, policy_cards,
)


def test_delete_policy():
    """LP-042: confirming Delete removes the policy and another policy is selected."""
    with sync_playwright() as p:
        browser, page = open_browser(p)
        open_leave_policies(page)
        name = unique_policy_name()
        try:
            create_policy(page, name)

            select_policy(page, name)
            detail_header(page).get_by_role("button", name="Delete", exact=True).click()
            delete_dialog(page).get_by_role("button", name="Delete", exact=True).click()
            expect_toast(page, "Leave policy deleted successfully.")
            expect(delete_dialog(page)).to_be_hidden()
            expect(policy_card(page, name)).to_have_count(0)
            expect(detail_name(page)).not_to_have_text(name)

            goto(page, POLICIES_URL)
            expect(policy_cards(page).first).to_be_visible()
            expect(policy_card(page, name)).to_have_count(0)
        finally:
            delete_policy(page, name)

        browser.close()
