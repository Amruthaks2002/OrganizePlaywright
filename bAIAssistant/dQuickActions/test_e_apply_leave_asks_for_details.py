from playwright.sync_api import sync_playwright
from utils.ai_assistant_helper import (open_ai_as_employee, click_quick_action, reply_text, table_headers,
                                       sent_message, leave_request_ids, new_leave_requests, BALANCE_COLUMNS)


def test_apply_leave_asks_for_details():
    """AI-030: The Apply Leave quick action shows the balances and asks for the leave type, dates, full / half day
    and reason - without submitting anything yet."""
    with sync_playwright() as p:
        browser, page = open_ai_as_employee(p)
        before = leave_request_ids(page)

        reply, response = click_quick_action(page, "Apply Leave")
        text = reply_text(reply).lower()

        assert "apply" in sent_message(response).lower()
        assert table_headers(reply) == BALANCE_COLUMNS
        for detail in ["leave type", "date", "half day", "reason"]:
            assert detail in text, f"the reply doesn't ask for the {detail}: {reply_text(reply)}"
        assert new_leave_requests(page, before) == [], "Apply Leave submitted a request without any details"

        browser.close()
