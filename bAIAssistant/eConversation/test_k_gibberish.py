import pytest
from playwright.sync_api import sync_playwright
from utils.ai_assistant_helper import open_ai_as_employee, ask, reply_text, leave_request_ids, new_leave_requests, \
    ERROR_REPLY


@pytest.mark.parametrize("message", ["asdkjh qwezx zzzpq", "?"], ids=["gibberish", "single-char"])
def test_gibberish(message):
    """AI-043: Gibberish or a lone "?" gets a polite clarification - no error, no data table, nothing submitted."""
    with sync_playwright() as p:
        browser, page = open_ai_as_employee(p)
        before = leave_request_ids(page)

        reply, response = ask(page, message)

        assert response.status == 200
        assert reply_text(reply) and reply_text(reply) != ERROR_REPLY
        assert new_leave_requests(page, before) == [], "a leave was submitted"

        browser.close()
