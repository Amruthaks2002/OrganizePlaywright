from playwright.sync_api import sync_playwright, expect
from utils.leave_policy_helper import (
    open_browser, open_leave_policies, unique_policy_name, create_policy, delete_policy,
    select_policy, detail_header, delete_dialog, policy_card, goto, POLICIES_URL,
)


def test_close_delete_dialog_with_x():
    """LP-044: closing the delete confirmation with X keeps the policy."""
    with sync_playwright() as p:
        browser, page = open_browser(p)
        open_leave_policies(page)
        name = unique_policy_name()
        try:
            create_policy(page, name)

            select_policy(page, name)
            detail_header(page).get_by_role("button", name="Delete", exact=True).click()
            delete_dialog(page).get_by_role("button", name="Close").click()
            expect(delete_dialog(page)).to_be_hidden()

            goto(page, POLICIES_URL)
            expect(policy_card(page, name)).to_have_count(1)
        finally:
            delete_policy(page, name)

        browser.close()
