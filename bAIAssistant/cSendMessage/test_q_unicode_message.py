from playwright.sync_api import sync_playwright, expect
from utils.ai_assistant_helper import open_ai_as_employee, ask, reply_text, user_messages, sent_message, ERROR_REPLY

MESSAGE = "എന്റെ ലീവ് ബാലൻസ് എത്ര? 🌴 Combien de congés me reste-t-il ?"


def test_unicode_message():
    """AI-024: Emoji and non-Latin text (Malayalam, French accents) are sent and shown unchanged, and get a reply."""
    with sync_playwright() as p:
        browser, page = open_ai_as_employee(p)

        reply, response = ask(page, MESSAGE)

        assert sent_message(response) == MESSAGE
        assert response.json()["data"]["user_message"] == MESSAGE
        expect(user_messages(page)).to_have_text([MESSAGE])
        assert reply_text(reply) and reply_text(reply) != ERROR_REPLY

        browser.close()
