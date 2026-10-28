from playwright.sync_api import sync_playwright, expect
from utils.ai_assistant_helper import (open_ai_as_employee, wait_for_reply, reply_text, replies, textarea,
                                       send_button, user_messages, sent_message, ERROR_REPLY, SEND_URL, REPLY_TIMEOUT)

QUESTION = "What is my current WFH balance?"


def test_send_with_button():
    """AI-010: The send (arrow) button sends the message just like Enter does."""
    with sync_playwright() as p:
        browser, page = open_ai_as_employee(p)

        textarea(page).fill(QUESTION)
        expect(send_button(page)).to_be_enabled()
        with page.expect_response(SEND_URL, timeout=REPLY_TIMEOUT) as response_info:
            send_button(page).click()
        reply = wait_for_reply(page, 0)

        assert sent_message(response_info.value) == QUESTION
        expect(user_messages(page)).to_have_text([QUESTION])
        expect(textarea(page)).to_have_value("")
        assert reply_text(reply) != ERROR_REPLY
        expect(replies(page)).to_have_count(1)

        browser.close()
