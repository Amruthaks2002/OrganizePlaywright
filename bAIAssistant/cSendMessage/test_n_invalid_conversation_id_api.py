from playwright.sync_api import sync_playwright
from utils.ai_assistant_helper import open_ai_as_employee, api_send, CONVERSATION_ID_INVALID


def test_invalid_conversation_id_api():
    """AI-021: /ai/send with a conversation_id that isn't a UUID returns 422."""
    with sync_playwright() as p:
        browser, page = open_ai_as_employee(p)

        response = api_send(page, {"message": "hi", "conversation_id": "not-a-uuid"})

        assert response.status == 422
        assert response.json()["errors"]["conversation_id"] == [CONVERSATION_ID_INVALID]

        browser.close()
