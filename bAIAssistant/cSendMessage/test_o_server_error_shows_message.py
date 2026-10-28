from playwright.sync_api import sync_playwright, expect
from utils.ai_assistant_helper import (open_ai_as_employee, ask, reply_text, textarea, send_button, mic_button,
                                       typing_indicator, ERROR_REPLY, SEND_URL)


def test_server_error_shows_message():
    """AI-022: When /ai/send fails (mocked 500) the chat shows "Something went wrong. Please try again." and the
    input works again for the next message."""
    with sync_playwright() as p:
        browser, page = open_ai_as_employee(p)
        page.route(SEND_URL, lambda route: route.fulfill(status=500, body="{}"))

        reply, _ = ask(page, "What is my current leave balance?")

        assert reply_text(reply) == ERROR_REPLY
        expect(typing_indicator(page)).to_have_count(0)
        expect(mic_button(page)).to_be_enabled()
        textarea(page).fill("Show me my leave history.")
        expect(send_button(page)).to_be_enabled()

        browser.close()
