from playwright.sync_api import sync_playwright, expect
from utils.ai_assistant_helper import open_ai_as_employee, expect_welcome_loaded, ask, replies, user_messages


def test_reload_starts_new_conversation():
    """AI-018: Reloading the page clears the chat, and the next message starts a new conversation."""
    with sync_playwright() as p:
        browser, page = open_ai_as_employee(p)
        _, first = ask(page, "What is my current leave balance?")
        first_conversation = first.json()["data"]["conversation_id"]  # the body is gone after the reload

        page.reload()
        expect_welcome_loaded(page)
        expect(user_messages(page)).to_have_count(0)
        expect(replies(page)).to_have_count(0)

        _, second = ask(page, "Show me my leave history.")
        assert second.request.post_data_json["conversation_id"] is None
        assert second.json()["data"]["conversation_id"] != first_conversation

        browser.close()
