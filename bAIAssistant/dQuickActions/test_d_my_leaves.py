from playwright.sync_api import sync_playwright
from utils.ai_assistant_helper import (open_ai_as_employee, click_quick_action, reply_text, sent_message,
                                       approved_leave_dates, shown_as)


def test_my_leaves():
    """AI-029: The My Leaves quick action asks for the leave history and the reply lists the employee's requests."""
    with sync_playwright() as p:
        browser, page = open_ai_as_employee(p)

        reply, response = click_quick_action(page, "My Leaves")
        text = reply_text(reply)
        approved = approved_leave_dates(page)

        assert "history" in sent_message(response).lower()
        assert "leave" in text.lower()
        assert approved, "the AI test account has no approved leave to look for"
        assert shown_as(approved[-1]).search(text), f"the approved leave on {approved[-1]} isn't in the history: {text}"

        browser.close()
