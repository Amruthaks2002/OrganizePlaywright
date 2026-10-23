from playwright.sync_api import sync_playwright
from utils.leave_policy_helper import (
    open_browser, open_leave_policies, policy_cards, card_name, card_employee_count,
    select_policy, employees_count,
)


def test_employee_count_matches():
    """LP-005: the employee count on each card matches the Employees count in the detail panel."""
    with sync_playwright() as p:
        browser, page = open_browser(p)
        open_leave_policies(page)

        for card in policy_cards(page).all():
            name = card_name(card).inner_text().strip()
            select_policy(page, name)
            assert employees_count(page) == card_employee_count(card), name

        browser.close()
