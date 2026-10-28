from playwright.sync_api import sync_playwright
from utils.ai_assistant_helper import launch, SEND_URL, BASE_URL


def test_logged_out_cannot_send():
    """AI-004: A signed-out POST to /ai/send is rejected (401, or 419 for the missing CSRF session) with no AI reply."""
    with sync_playwright() as p:
        browser, page = launch(p)
        page.goto(BASE_URL)  # a guest session, so the request carries real cookies

        response = page.request.post(SEND_URL, data={"message": "What is my leave balance?"},
                                     headers={"Accept": "application/json"})

        assert response.status in (401, 419), f"expected 401/419, got {response.status}"
        assert "reply" not in response.text()

        browser.close()
