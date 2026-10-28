from playwright.sync_api import sync_playwright, expect
from utils.ai_assistant_helper import (open_ai_as_employee, wait_for_reply, textarea, send_button, mic_button,
                                       quick_action, typing_indicator, user_messages, QUICK_ACTIONS, SEND_URL)


def test_controls_locked_while_waiting():
    """AI-014: While a reply is pending the typing indicator shows, send / mic / quick actions are locked,
    and pressing Enter again doesn't send a duplicate."""
    with sync_playwright() as p:
        browser, page = open_ai_as_employee(p)
        sent = []
        page.on("request", lambda r: sent.append(r) if r.url == SEND_URL else None)

        textarea(page).fill("What is my current leave balance?")
        textarea(page).press("Enter")

        expect(typing_indicator(page)).to_be_visible()
        expect(mic_button(page)).to_be_disabled()
        textarea(page).fill("Show me my leave history.")
        expect(send_button(page)).to_be_disabled()
        textarea(page).press("Enter")
        quick_action(page, QUICK_ACTIONS[2]).click()

        wait_for_reply(page, 0)
        page.wait_for_timeout(1500)
        assert len(sent) == 1, f"expected one /ai/send while the first was pending, got {len(sent)}"
        expect(user_messages(page)).to_have_count(1)

        browser.close()
