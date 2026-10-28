import re

from playwright.sync_api import sync_playwright, expect
from utils.ai_assistant_helper import open_ai_as_employee, click_quick_action, copy_buttons


def test_copy_reply_text():
    """AI-045: Every reply has a Copy Text button that copies the reply as plain text, without HTML tags."""
    with sync_playwright() as p:
        browser, page = open_ai_as_employee(p)
        page.context.grant_permissions(["clipboard-read", "clipboard-write"])

        reply, _ = click_quick_action(page, "Leave Balance")
        expect(copy_buttons(page)).to_have_count(1)
        copy_buttons(page).last.click()
        copied = page.evaluate("() => navigator.clipboard.readText()")

        assert copied == re.sub(r"<[^>]+>", "", reply.inner_html())
        assert not re.search(r"<\w+", copied), f"HTML tags were copied: {copied[:200]}"
        assert "Remaining" in copied

        browser.close()
