from playwright.sync_api import sync_playwright, expect
from utils.ai_assistant_helper import open_ai_as_employee, click_quick_action, ask, quick_action, user_messages


def test_scrolls_to_latest():
    """AI-047: After several long replies the chat is scrolled to the newest message."""
    with sync_playwright() as p:
        browser, page = open_ai_as_employee(p)

        click_quick_action(page, "Leave Balance")
        click_quick_action(page, "Apply Leave")
        reply, _ = ask(page, "Show me my leave history.")

        expect(reply).to_be_in_viewport()
        expect(user_messages(page).last).to_have_text("Show me my leave history.")
        expect(quick_action(page, "Leave Balance")).not_to_be_in_viewport()

        browser.close()
