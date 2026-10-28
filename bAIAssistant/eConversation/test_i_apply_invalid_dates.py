from datetime import date, timedelta

import pytest
from playwright.sync_api import sync_playwright
from utils.ai_assistant_helper import (open_ai_as_employee, ask, reply_text, leave_request_ids, new_leave_requests,
                                       cancel_new_leaves, future_working_days, spoken, qa_reason, unique_tag)


def past_working_day():
    day = date.today() - timedelta(days=30)
    while day.isoweekday() > 5:
        day -= timedelta(days=1)
    return day


@pytest.mark.parametrize("case", ["past-date", "end-before-start"])
def test_apply_invalid_dates(case):
    """AI-041: A leave in the past, or ending before it starts, isn't submitted and the reply explains why."""
    with sync_playwright() as p:
        browser, page = open_ai_as_employee(p)
        before = leave_request_ids(page)
        if case == "past-date":
            period = f"on {spoken(past_working_day())}, full day"
        else:
            start, _, end = future_working_days(page, 3, days_ahead=105)
            period = f"starting {spoken(end)} and ending {spoken(start)}, full days"
        tag = unique_tag()
        try:
            # judge the first answer on its own - don't confirm any corrected dates it suggests
            reply, _ = ask(page, f"Apply compensatory leave {period}. Reason: {qa_reason(tag)}.")

            assert new_leave_requests(page, before, tag) == [], f"an invalid leave ({case}) was submitted"
            assert "submitted successfully" not in reply_text(reply).lower()
        finally:
            cancel_new_leaves(page, before, tag)

        browser.close()
