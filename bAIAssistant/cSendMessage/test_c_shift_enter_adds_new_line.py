from playwright.sync_api import sync_playwright, expect
from utils.ai_assistant_helper import open_ai_as_employee, textarea, user_messages, SEND_URL


def test_shift_enter_adds_new_line():
    """AI-011: Shift+Enter adds a new line in the textarea and doesn't send anything."""
    with sync_playwright() as p:
        browser, page = open_ai_as_employee(p)
        sent = []
        page.on("request", lambda r: sent.append(r) if r.url == SEND_URL else None)

        textarea(page).click()
        textarea(page).type("Line one")
        textarea(page).press("Shift+Enter")
        textarea(page).type("Line two")
        page.wait_for_timeout(1500)

        expect(textarea(page)).to_have_value("Line one\nLine two")
        expect(user_messages(page)).to_have_count(0)
        assert not sent, "Shift+Enter must not send the message"

        browser.close()
