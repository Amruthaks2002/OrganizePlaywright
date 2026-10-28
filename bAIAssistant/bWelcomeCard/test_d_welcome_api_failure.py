from playwright.sync_api import sync_playwright, expect
from utils.ai_assistant_helper import (launch, login_employee, refresh_session, ask, reply_text, textarea,
                                       main_content, AI_URL, WELCOME_API_URL, ERROR_REPLY, DISCLAIMER)


def test_welcome_api_failure():
    """AI-008: When the welcome-message API fails (mocked 500) the page still loads and the chat still works."""
    with sync_playwright() as p:
        browser, page = launch(p)
        login_employee(page)
        refresh_session(page)
        page.route(WELCOME_API_URL, lambda route: route.fulfill(status=500, body="{}"))

        page.goto(AI_URL)
        expect(main_content(page).get_by_text(DISCLAIMER)).to_be_visible()
        expect(textarea(page)).to_be_editable()

        reply, _ = ask(page, "What is my current leave balance?")
        assert reply_text(reply) and reply_text(reply) != ERROR_REPLY

        browser.close()
