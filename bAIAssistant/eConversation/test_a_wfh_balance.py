from playwright.sync_api import sync_playwright
from utils.ai_assistant_helper import open_ai_as_employee, ask, reply_text, table_rows


def test_wfh_balance():
    """AI-033: Asking for the WFH balance returns the work modes with a Work From Home row."""
    with sync_playwright() as p:
        browser, page = open_ai_as_employee(p)

        reply, _ = ask(page, "What is my current WFH balance?")

        assert "work from home" in reply_text(reply).lower()
        modes = [list(row.values())[0] for row in table_rows(reply)]
        assert "Work From Home" in modes, f"no Work From Home row in {modes}"

        browser.close()
