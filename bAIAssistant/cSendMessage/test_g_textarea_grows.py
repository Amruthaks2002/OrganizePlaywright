from playwright.sync_api import sync_playwright
from utils.ai_assistant_helper import open_ai_as_employee, textarea

MAX_HEIGHT = 192  # max-h-48


def test_textarea_grows():
    """AI-015: The textarea grows with multi-line text and stops at its max height, scrolling after that."""
    with sync_playwright() as p:
        browser, page = open_ai_as_employee(p)
        box = textarea(page)

        one_line = box.evaluate("t => t.clientHeight")
        box.fill("line 1\nline 2\nline 3")
        three_lines = box.evaluate("t => t.clientHeight")
        box.fill("\n".join(f"line {i}" for i in range(1, 31)))
        thirty_lines = box.evaluate("t => ({height: t.clientHeight, scroll: t.scrollHeight})")

        assert three_lines > one_line, f"textarea didn't grow: {one_line} -> {three_lines}"
        assert thirty_lines["height"] <= MAX_HEIGHT, f"textarea grew past {MAX_HEIGHT}px: {thirty_lines}"
        assert thirty_lines["scroll"] > thirty_lines["height"], "long text should scroll inside the textarea"

        browser.close()
