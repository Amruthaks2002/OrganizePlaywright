from playwright.sync_api import sync_playwright
from utils.ai_assistant_helper import open_ai_as_employee, ask, reply_text


def test_conversation_is_kept():
    """AI-017: The first message starts a conversation (conversation_id null); follow-ups send the id the first
    reply returned, so the assistant keeps the context."""
    with sync_playwright() as p:
        browser, page = open_ai_as_employee(p)

        _, first = ask(page, "What is my current leave balance?")
        conversation_id = first.json()["data"]["conversation_id"]
        reply, second = ask(page, "Of those, how many sick leave days do I have remaining?")

        assert first.request.post_data_json["conversation_id"] is None
        assert conversation_id
        assert second.request.post_data_json["conversation_id"] == conversation_id
        assert second.json()["data"]["conversation_id"] == conversation_id
        assert "sick" in reply_text(reply).lower(), f"follow-up lost the context: {reply_text(reply)}"

        browser.close()
