import re

from playwright.sync_api import sync_playwright
from utils.ai_assistant_helper import (open_ai_as_employee, ask, reply_text, leave_request_ids, leave_balance_cards,
                                       new_leave_requests, cancel_new_leaves, future_working_days, spoken, qa_reason,
                                       unique_tag)

EXPLAINS_BALANCE = re.compile(r"balance|left|only|more than|exceed|insufficient", re.I)


def test_apply_more_than_balance():
    """AI-040: Asking for more days of a leave type than are left is refused (the assistant may offer alternatives)
    and no request is created."""
    with sync_playwright() as p:
        browser, page = open_ai_as_employee(p)
        before = leave_request_ids(page)
        balances = leave_balance_cards(page)
        leave_type = min((t for t in balances if balances[t] > 0), key=lambda t: balances[t])
        days = future_working_days(page, int(balances[leave_type]) + 2, days_ahead=75)
        tag = unique_tag()
        try:
            # judge the first answer on its own - don't confirm any alternative it offers
            reply, _ = ask(page, f"Apply {leave_type} leave from {spoken(days[0])} to {spoken(days[-1])}, full days. "
                                 f"Reason: {qa_reason(tag)}.")

            assert new_leave_requests(page, before, tag) == [], (
                f"{len(days)} days of {leave_type} were accepted with only {balances[leave_type]} left")
            assert EXPLAINS_BALANCE.search(reply_text(reply)), reply_text(reply)
        finally:
            cancel_new_leaves(page, before, tag)

        browser.close()
