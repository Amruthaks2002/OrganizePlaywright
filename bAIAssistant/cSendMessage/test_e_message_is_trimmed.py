from playwright.sync_api import sync_playwright, expect
from utils.ai_assistant_helper import open_ai_as_employee, ask, user_messages, sent_message


def test_message_is_trimmed():
    """AI-013: Leading / trailing spaces and new lines are trimmed from the message shown and sent."""
    with sync_playwright() as p:
        browser, page = open_ai_as_employee(p)

        _, response = ask(page, "   \n  Show me my leave history.  \n ")

        assert sent_message(response) == "Show me my leave history."
        expect(user_messages(page)).to_have_text(["Show me my leave history."])

        browser.close()
