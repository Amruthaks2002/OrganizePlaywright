from playwright.sync_api import sync_playwright
from utils.ai_assistant_helper import (open_ai_as_employee, apply_leave_via_ai, leave_request_ids, new_leave_requests,
                                       cancel_new_leaves, future_working_days, spoken, qa_reason, unique_tag)


def test_apply_half_day_leave():
    """AI-042: Applying a morning half-day compensatory leave through the chat creates a pending half-day request
    for the first session. The request is cancelled afterwards."""
    with sync_playwright() as p:
        browser, page = open_ai_as_employee(p)
        before = leave_request_ids(page)
        day = future_working_days(page, 1, days_ahead=60)[0]
        tag = unique_tag()
        try:
            apply_leave_via_ai(page, f"Apply compensatory leave on {spoken(day)}, half day in the morning "
                                     f"(first half). Reason: {qa_reason(tag)}.", before, tag)

            created = new_leave_requests(page, before, tag)
            assert len(created) == 1, f"expected one new leave request, got {created}"
            leave = created[0]
            assert leave["start_date"] == day.isoformat()
            assert leave["day_type"] == "half"
            assert leave["start_half_session"] == "first_session"
            assert leave["status"] == "pending"
        finally:
            cancel_new_leaves(page, before, tag)

        browser.close()
