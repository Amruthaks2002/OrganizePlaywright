from playwright.sync_api import sync_playwright, expect
from utils.ai_assistant_helper import open_ai_as_employee, ask, user_messages, main_content

PAYLOAD = "<img src=x onerror=\"window.__xss = 1\"><b>bold</b> what is my leave balance?"


def test_html_in_message_is_text():
    """AI-023: HTML typed into a message is shown as plain text in the "You" bubble and never runs."""
    with sync_playwright() as p:
        browser, page = open_ai_as_employee(p)
        dialogs = []
        page.on("dialog", lambda d: (dialogs.append(d.message), d.dismiss()))

        ask(page, PAYLOAD)

        expect(user_messages(page).last).to_have_text(PAYLOAD)
        assert user_messages(page).last.locator("img, b").count() == 0
        # the reply is rendered as HTML, so check the echoed payload didn't run there either
        assert page.evaluate("() => window.__xss") is None, "the onerror handler ran"
        assert main_content(page).locator("img[src='x']").count() == 0
        assert not dialogs

        browser.close()
