from playwright.sync_api import sync_playwright, expect
from utils.ai_assistant_helper import (open_ai_as_employee, click_quick_action, table_headers, user_messages,
                                       sent_message, BALANCE_COLUMNS)


def test_leave_balance_table():
    """AI-026: The Leave Balance quick action asks for the balance and the reply has a table with
    Leave Type / Total / Taken / Remaining."""
    with sync_playwright() as p:
        browser, page = open_ai_as_employee(p)

        reply, response = click_quick_action(page, "Leave Balance")

        expect(user_messages(page)).to_have_text([sent_message(response)])
        assert "balance" in sent_message(response).lower()
        assert table_headers(reply) == BALANCE_COLUMNS
        assert reply.locator("table tbody tr").count() > 0

        browser.close()
