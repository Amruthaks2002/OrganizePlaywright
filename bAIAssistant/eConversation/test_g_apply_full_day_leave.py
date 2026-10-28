from playwright.sync_api import sync_playwright
from utils.ai_assistant_helper import (open_ai_as_employee, apply_leave_via_ai, ask, reply_text, leave_request_ids,
                                       new_leave_requests, cancel_new_leaves, future_working_days, spoken, shown_as,
                                       qa_reason, unique_tag)


def test_apply_full_day_leave():
    """AI-039: Applying a full-day compensatory leave through the chat creates a pending request with those details,
    and it shows in My Leaves. The request is cancelled afterwards."""
    with sync_playwright() as p:
        browser, page = open_ai_as_employee(p)
        before = leave_request_ids(page)
        # each Apply Leave test books its own stretch of dates so parallel runs don't overlap
        day = future_working_days(page, 1, days_ahead=45)[0]
        tag = unique_tag()
        try:
            apply_leave_via_ai(page, f"Apply compensatory leave on {spoken(day)}, full day. "
                                     f"Reason: {qa_reason(tag)}.", before, tag)

            created = new_leave_requests(page, before, tag)
            assert len(created) == 1, f"expected one new leave request, got {created}"
            leave = created[0]
            assert leave["start_date"] == leave["end_date"] == day.isoformat()
            assert leave["leave_type"]["name"].lower() == "compensatory"
            assert leave["day_type"] == "full"
            assert leave["status"] == "pending"

            history, _ = ask(page, "Show me my leave history.")
            assert shown_as(day).search(reply_text(history)), f"{day} isn't in My Leaves: {reply_text(history)}"
        finally:
            cancel_new_leaves(page, before, tag)

        browser.close()
