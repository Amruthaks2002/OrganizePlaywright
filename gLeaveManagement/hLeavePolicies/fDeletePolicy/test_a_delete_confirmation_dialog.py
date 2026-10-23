from playwright.sync_api import sync_playwright, expect
from utils.leave_policy_helper import (
    open_browser, open_leave_policies, unique_policy_name, create_policy, delete_policy,
    select_policy, detail_header, delete_dialog,
)


def test_delete_confirmation_dialog():
    """LP-041: Delete opens a confirmation naming the policy and warning about its leave types."""
    with sync_playwright() as p:
        browser, page = open_browser(p)
        open_leave_policies(page)
        name = unique_policy_name()
        try:
            create_policy(page, name)

            select_policy(page, name)
            detail_header(page).get_by_role("button", name="Delete", exact=True).click()
            confirm = delete_dialog(page)
            expect(confirm.get_by_role("heading", name="Delete Leave Policy")).to_be_visible()
            expect(confirm.get_by_text(
                f'Are you sure you want to delete "{name}"? All associated leave types will also be removed.'
            )).to_be_visible()
            expect(confirm.get_by_role("button", name="Cancel")).to_be_visible()
            expect(confirm.get_by_role("button", name="Delete", exact=True)).to_be_visible()
            confirm.get_by_role("button", name="Cancel").click()
            expect(confirm).to_be_hidden()
        finally:
            delete_policy(page, name)

        browser.close()
