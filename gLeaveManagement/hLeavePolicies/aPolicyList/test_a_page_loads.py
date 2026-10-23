import re
from playwright.sync_api import sync_playwright, expect
from utils.leave_policy_helper import open_browser, open_leave_policies, main_content, policy_cards


def test_page_loads():
    """LP-001: Leave Management > Leave Policies opens the policies page."""
    with sync_playwright() as p:
        browser, page = open_browser(p)
        open_leave_policies(page)
        main = main_content(page)

        expect(page).to_have_url(re.compile(r"/leave-policies$"))
        expect(main.get_by_role("heading", name="Leave Policies", level=1)).to_be_visible()
        expect(main.get_by_text("Manage policies and their leave types")).to_be_visible()
        expect(main.get_by_role("button", name="Create Policy")).to_be_visible()
        expect(policy_cards(page).first).to_be_visible()

        browser.close()
