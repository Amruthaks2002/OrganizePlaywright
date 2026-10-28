from playwright.sync_api import sync_playwright
from utils.ai_assistant_helper import open_ai_as_employee, ask, reply_text, ERROR_REPLY, OUT_OF_SCOPE_REPLY


def test_attendance():
    """AI-035: Attendance is a supported topic - asking about it gets an attendance answer, not the out-of-scope message."""
    with sync_playwright() as p:
        browser, page = open_ai_as_employee(p)

        reply, _ = ask(page, "Show my attendance for this month.")
        text = reply_text(reply).lower()

        assert text != ERROR_REPLY.lower()
        assert OUT_OF_SCOPE_REPLY not in text
        assert "attendance" in text, f"reply isn't about attendance: {reply_text(reply)}"

        browser.close()
