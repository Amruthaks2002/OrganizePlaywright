import time
from playwright.sync_api import sync_playwright
from utils.ai_assistant_helper import (open_ai_as_employee, textarea, replies, wait_for_reply, reply_text,
                                       MAX_MESSAGE_LENGTH, SEND_URL)


def test_message_length_limit_ui():
    """AI-019b (likely bug): a message over 5000 characters is either cut off at 5000 by the textarea or answered
    with the length limit. Today the textarea has no maxlength, the server's 422 is swallowed and the chat only
    shows the generic "Something went wrong"."""
    with sync_playwright() as p:
        browser, page = open_ai_as_employee(p)
        statuses = []
        page.on("response", lambda r: statuses.append(r.status) if r.url == SEND_URL else None)

        textarea(page).fill("x" * (MAX_MESSAGE_LENGTH + 1))
        kept = len(textarea(page).input_value())
        if kept <= MAX_MESSAGE_LENGTH:
            browser.close()
            return  # the textarea enforces the limit

        before = replies(page).count()
        textarea(page).press("Enter")
        reply = wait_for_reply(page, before)
        time.sleep(8)

        assert "5000" in reply_text(reply), (
            f"the {MAX_MESSAGE_LENGTH} character limit isn't shown (server answered {statuses}): {reply_text(reply)!r}")

        browser.close()
