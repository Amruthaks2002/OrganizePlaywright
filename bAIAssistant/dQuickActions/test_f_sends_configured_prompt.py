import pytest
from playwright.sync_api import sync_playwright
from utils.ai_assistant_helper import (open_ai_as_employee, quick_action, wait_for_reply, sent_message,
                                       WELCOME_API_URL, SEND_URL, REPLY_TIMEOUT, QUICK_ACTIONS)


@pytest.mark.parametrize("label", QUICK_ACTIONS)
def test_sends_configured_prompt(label):
    """AI-031 (likely bug): a quick action sends the action_prompt configured for it in AI Assistant Settings.
    Today the page swaps in hard-coded text for the built-in labels (e.g. "View my leave balance." is configured,
    "What is my current leave balance?" is sent)."""
    with sync_playwright() as p:
        browser, page = open_ai_as_employee(p)
        actions = page.request.get(WELCOME_API_URL, headers={"Accept": "application/json"}).json()["actions"]
        configured = next(a["action_prompt"] for a in actions if a["label"] == label)

        with page.expect_response(SEND_URL, timeout=REPLY_TIMEOUT) as response_info:
            quick_action(page, label).click()
        wait_for_reply(page, 0)

        assert sent_message(response_info.value) == configured

        browser.close()
