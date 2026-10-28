from playwright.sync_api import sync_playwright, expect
from utils.ai_assistant_helper import open_ai_as_employee, textarea, mic_button, typing_indicator, wait_for_reply


def test_mic_locked_while_waiting():
    """AI-052: The mic is disabled while a reply is pending and enabled again once it arrives."""
    with sync_playwright() as p:
        browser, page = open_ai_as_employee(p)

        textarea(page).fill("What is my current leave balance?")
        textarea(page).press("Enter")
        expect(typing_indicator(page)).to_be_visible()
        expect(mic_button(page)).to_be_disabled()

        wait_for_reply(page, 0)
        expect(mic_button(page)).to_be_enabled()

        browser.close()
