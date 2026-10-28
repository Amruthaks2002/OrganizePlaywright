from playwright.sync_api import sync_playwright, expect
from utils.ai_assistant_helper import open_ai_as_employee, quick_action, wait_for_reply, user_messages, SEND_URL


def test_double_click_sends_once():
    """AI-032: Clicking quick actions again while a reply is pending doesn't send another message."""
    with sync_playwright() as p:
        browser, page = open_ai_as_employee(p)
        sent = []
        page.on("request", lambda r: sent.append(r) if r.url == SEND_URL else None)

        quick_action(page, "Leave Balance").click()
        quick_action(page, "Leave Balance").click()
        quick_action(page, "My Leaves").click()
        wait_for_reply(page, 0)
        page.wait_for_timeout(1500)

        assert len(sent) == 1, f"expected one /ai/send, got {len(sent)}"
        expect(user_messages(page)).to_have_count(1)

        browser.close()
