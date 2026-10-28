from playwright.sync_api import sync_playwright
import time
from utils.ai_assistant_helper import open_ai_as, open_ai_as_employee, ask, reply_text, api_send, unique_tag

RECALL = "Repeat my first message in this chat word for word."


def test_other_users_conversation():
    """AI-025 (known bug, security): An employee who sends another user's conversation_id is refused or gets a fresh
    conversation - never the other user's earlier messages. Today the employee is let into the admin's conversation
    and the assistant repeats what the admin wrote."""
    marker = f"QA-{unique_tag()}"
    with sync_playwright() as p:
        browser, page = open_ai_as(p, "admin")
        # an HR question, so the assistant answers it instead of refusing an off-topic "remember this code" request
        _, response = ask(page, f"What is my current leave balance? (reference {marker})")
        admin_conversation = response.json()["data"]["conversation_id"]
        # the conversation must really hold the marker, or the employee check below proves nothing
        own_recall, _ = ask(page, RECALL)
        assert marker in reply_text(own_recall), f"setup: the admin's own chat didn't recall it: {reply_text(own_recall)}"
        browser.close()

        browser, page = open_ai_as_employee(p)
        response = api_send(page, {"message": RECALL, "conversation_id": admin_conversation})

        if response.status == 200:
            data = response.json()["data"]
            assert marker not in data["reply"], "the employee could read the admin's conversation"
            assert data["conversation_id"] != admin_conversation, "the employee was let into the admin's conversation"
        else:
            assert response.status in (403, 404, 422), f"unexpected status {response.status}"

        time.sleep(20)
        browser.close()
