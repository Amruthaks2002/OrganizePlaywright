import pytest
from playwright.sync_api import sync_playwright, expect
from utils.ai_assistant_helper import open_ai_as_employee, textarea, send_button, user_messages, SEND_URL


@pytest.mark.parametrize("text", ["", "     ", "\n\n", " \n \t "], ids=["empty", "spaces", "new-lines", "mixed"])
def test_blank_message_not_sent(text):
    """AI-012: The send button stays disabled for an empty / whitespace-only message, and Enter doesn't send it."""
    with sync_playwright() as p:
        browser, page = open_ai_as_employee(p)
        sent = []
        page.on("request", lambda r: sent.append(r) if r.url == SEND_URL else None)

        textarea(page).fill(text)
        expect(send_button(page)).to_be_disabled()
        textarea(page).press("Enter")
        page.wait_for_timeout(1500)

        expect(user_messages(page)).to_have_count(0)
        assert not sent, f"a blank message ({text!r}) must not be sent"

        browser.close()
