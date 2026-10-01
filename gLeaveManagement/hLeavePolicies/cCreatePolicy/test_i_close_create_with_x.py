from playwright.sync_api import sync_playwright, expect
from utils.leave_policy_helper import (
    open_browser, open_leave_policies, unique_policy_name, open_create_form, fill_policy_form,
    policy_card, delete_policy, goto, POLICIES_URL, policy_cards, dialog, close_x,
)


def test_close_create_with_x():
    """LP-023: the X button closes the Create Policy form without creating anything."""
    with sync_playwright() as p:
        browser, page = open_browser(p)
        open_leave_policies(page)
        name = unique_policy_name()
        try:
            form = open_create_form(page)
            fill_policy_form(form, name=name)
            close_x(dialog(page, "Create Policy")).click()
            expect(form).to_be_hidden()

            goto(page, POLICIES_URL)
            expect(policy_cards(page).first).to_be_visible()
            expect(policy_card(page, name)).to_have_count(0)
        finally:
            delete_policy(page, name)

        browser.close()
