from playwright.sync_api import sync_playwright
from utils.ai_assistant_helper import launch, AI_URL, WELCOME_API_URL, BASE_URL


def test_logged_out_redirects_to_login():
    """AI-003: Someone who isn't signed in is sent to /login from /ai, and the welcome-message API returns 401."""
    with sync_playwright() as p:
        browser, page = launch(p)

        page.goto(AI_URL)
        assert page.url == f"{BASE_URL}/login"

        response = page.request.get(WELCOME_API_URL, headers={"Accept": "application/json"})
        assert response.status == 401

        browser.close()
