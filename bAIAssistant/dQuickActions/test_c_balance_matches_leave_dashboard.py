from playwright.sync_api import sync_playwright
import time
from utils.ai_assistant_helper import (open_ai_as_employee, click_quick_action, balance_table, leave_balance_cards,
                                       normalise_leave_type)


def test_balance_matches_leave_dashboard():
    """AI-028: The remaining days the assistant reports match the Available figure on the employee's Leave Dashboard."""
    with sync_playwright() as p:
        browser, page = open_ai_as_employee(p)

        reply, _ = click_quick_action(page, "Leave Balance")
        ai = {normalise_leave_type(k): remaining for k, (_, _, remaining) in balance_table(reply).items()}
        dashboard = leave_balance_cards(page)

        time.sleep(10)

        assert set(dashboard) <= set(ai), f"leave types missing from the AI reply: {set(dashboard) - set(ai)}"
        for leave_type, available in dashboard.items():
            assert ai[leave_type] == available, f"{leave_type}: AI says {ai[leave_type]}, dashboard says {available}"

        browser.close()
