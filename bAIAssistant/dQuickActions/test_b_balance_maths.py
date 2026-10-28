from playwright.sync_api import sync_playwright
from utils.ai_assistant_helper import open_ai_as_employee, click_quick_action, balance_table


def test_balance_maths():
    """AI-027: In the balance table Remaining = Total - Taken for every leave type, half days included."""
    with sync_playwright() as p:
        browser, page = open_ai_as_employee(p)

        reply, _ = click_quick_action(page, "Leave Balance")
        balances = balance_table(reply)

        assert balances, "the balance table is empty"
        for leave_type, (total, taken, remaining) in balances.items():
            assert remaining == total - taken, f"{leave_type}: {total} - {taken} should be {total - taken}, got {remaining}"

        browser.close()
