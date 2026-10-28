from playwright.sync_api import sync_playwright, expect
from utils.ai_assistant_helper import open_ai_as_employee, ask, textarea


def test_focus_returns_after_reply():
    """AI-016: After a reply arrives the cursor is back in the textarea, ready for the next question."""
    with sync_playwright() as p:
        browser, page = open_ai_as_employee(p)

        ask(page, "What is my current leave balance?")

        expect(textarea(page)).to_be_focused()

        browser.close()
