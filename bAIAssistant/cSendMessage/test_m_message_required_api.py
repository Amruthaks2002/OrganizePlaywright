import pytest
from playwright.sync_api import sync_playwright
from utils.ai_assistant_helper import open_ai_as_employee, api_send, MESSAGE_REQUIRED


@pytest.mark.parametrize("data", [{"message": ""}, {"message": "    "}, {}], ids=["empty", "spaces", "missing"])
def test_message_required_api(data):
    """AI-020: /ai/send with an empty, whitespace-only or missing message returns 422 "message field is required"."""
    with sync_playwright() as p:
        browser, page = open_ai_as_employee(p)

        response = api_send(page, data)

        assert response.status == 422
        assert response.json()["errors"]["message"] == [MESSAGE_REQUIRED]

        browser.close()
