from playwright.sync_api import sync_playwright, expect
from utils.leave_policy_helper import (
    open_browser, open_leave_policies, unique_policy_name, create_policy, delete_policy, policy_card,
    card_status, select_policy, detail_badges,
)


def test_create_inactive_policy():
    """LP-018: a policy created with Active switched off shows as Inactive."""
    with sync_playwright() as p:
        browser, page = open_browser(p)
        open_leave_policies(page)
        name = unique_policy_name()
        try:
            create_policy(page, name, active=False)

            expect(card_status(policy_card(page, name))).to_have_text("Inactive")
            select_policy(page, name)
            expect(detail_badges(page).first).to_have_text("Inactive")
        finally:
            delete_policy(page, name)

        browser.close()
