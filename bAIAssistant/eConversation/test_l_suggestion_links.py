import pytest
from playwright.sync_api import sync_playwright, expect
from utils.ai_assistant_helper import open_ai_as_employee, ask, wait_for_reply, user_messages, sent_message, SEND_URL, \
    REPLY_TIMEOUT


def test_suggestion_links():
    """AI-044: A suggestion in a reply (an element with data-action-prompt) sends its prompt when clicked."""
    with sync_playwright() as p:
        browser, page = open_ai_as_employee(p)

        reply, _ = ask(page, "What can you help me with?")
        suggestions = reply.locator("[data-action-prompt]")
        if suggestions.count() == 0:
            browser.close()
            pytest.skip("this reply came without suggestions")

        prompt = suggestions.first.get_attribute("data-action-prompt")
        with page.expect_response(SEND_URL, timeout=REPLY_TIMEOUT) as response_info:
            suggestions.first.click()
        wait_for_reply(page, 1)

        assert sent_message(response_info.value) == prompt.strip()
        expect(user_messages(page).last).to_have_text(prompt.strip())

        browser.close()
