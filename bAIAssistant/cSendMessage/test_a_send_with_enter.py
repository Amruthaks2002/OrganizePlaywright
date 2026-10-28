from playwright.sync_api import sync_playwright, expect
from utils.ai_assistant_helper import (open_ai_as_employee, ask, reply_text, textarea, user_messages,
                                       user_message_times, ERROR_REPLY, TIME_LABEL)

QUESTION = "What is my current leave balance?"


def test_send_with_enter():
    """AI-009: Typing a question and pressing Enter shows it as a "You" message with a time, an AI reply follows
    and the textarea is cleared."""
    with sync_playwright() as p:
        browser, page = open_ai_as_employee(p)

        reply, response = ask(page, QUESTION)

        assert response.status == 200
        expect(user_messages(page)).to_have_text([QUESTION])
        expect(user_message_times(page).first).to_have_text(TIME_LABEL)
        expect(textarea(page)).to_have_value("")
        assert reply_text(reply) and reply_text(reply) != ERROR_REPLY
        assert "leave" in reply_text(reply).lower()

        browser.close()
