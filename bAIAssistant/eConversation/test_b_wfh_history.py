from playwright.sync_api import sync_playwright
from utils.ai_assistant_helper import open_ai_as_employee, ask, reply_text, ERROR_REPLY, OUT_OF_SCOPE_REPLY


def test_wfh_history():
    """AI-034: Asking for the WFH history gets an answer about the employee's work-from-home requests."""
    with sync_playwright() as p:
        browser, page = open_ai_as_employee(p)

        reply, _ = ask(page, "Show me my WFH history.")
        text = reply_text(reply).lower()

        assert text != ERROR_REPLY.lower()
        assert OUT_OF_SCOPE_REPLY not in text
        assert "wfh" in text or "work from home" in text, f"reply isn't about WFH: {reply_text(reply)}"

        browser.close()
