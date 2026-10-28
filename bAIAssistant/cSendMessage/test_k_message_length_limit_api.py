from playwright.sync_api import sync_playwright
from utils.ai_assistant_helper import open_ai_as_employee, api_send, MAX_MESSAGE_LENGTH, MESSAGE_TOO_LONG

PREFIX = "What is my current leave balance? "


def padded(length):
    return (PREFIX + "x" * length)[:length]


def test_message_length_limit_api():
    """AI-019a: /ai/send accepts a message of exactly 5000 characters and rejects 5001 with 422."""
    with sync_playwright() as p:
        browser, page = open_ai_as_employee(p)

        at_limit = api_send(page, {"message": padded(MAX_MESSAGE_LENGTH)})
        over_limit = api_send(page, {"message": padded(MAX_MESSAGE_LENGTH + 1)})

        assert at_limit.status == 200, f"5000 chars should be accepted, got {at_limit.status}: {at_limit.text()[:200]}"
        assert over_limit.status == 422
        assert over_limit.json()["errors"]["message"] == [MESSAGE_TOO_LONG]

        browser.close()
