from playwright.sync_api import sync_playwright, expect
from utils.ai_assistant_helper import open_ai_as_employee, click_quick_action, reply_text


def test_formatting_rendered():
    """AI-046: Tables, numbered lists and bold text in a reply are rendered, not shown as raw HTML."""
    with sync_playwright() as p:
        browser, page = open_ai_as_employee(p)

        reply, _ = click_quick_action(page, "Apply Leave")

        expect(reply.locator("table thead th").first).to_be_visible()
        expect(reply.locator("table tbody tr").first).to_be_visible()
        expect(reply.locator("ol li, ul li").first).to_be_visible()
        expect(reply.locator("strong").first).to_be_visible()
        for tag in ["<p>", "<table>", "<strong>", "<li>", "</"]:
            assert tag not in reply_text(reply), f"raw {tag} shown in the reply"

        browser.close()
