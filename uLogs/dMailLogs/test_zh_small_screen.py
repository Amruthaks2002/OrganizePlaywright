"""ML-034: Phone and tablet widths.

Steps:
1. Log in as admin with a 390 x 844 (phone) window, then a 768 x 1024 (tablet) window.
2. Open /mail-logs.

Expected: the page doesn't scroll sideways (the table scrolls inside its own box), both dropdowns, both dates,
Reset and the first subject link can be reached, and rows are shown.
"""
import time

from playwright.sync_api import sync_playwright, expect
from utils.login_helper import login

BASE_URL = "https://organice.qc.iocod.com"
LOGS_URL = f"{BASE_URL}/mail-logs"
EMPTY_MESSAGE = "No mail has been sent yet."


SIZES = [(390, 844), (768, 1024)]


def test_ml_034_small_screen():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        problems = []
        for width, height in SIZES:
            page = browser.new_page(viewport={"width": width, "height": height})
            login(page)
            page.goto(LOGS_URL)
            page.get_by_role("heading", name="Mail Logs").wait_for(state="visible")
            time.sleep(1)
            if not page.evaluate("document.documentElement.scrollWidth <= window.innerWidth"):
                problems.append(f"{width}px: the page scrolls sideways")
            wrapper = page.locator("table").first.evaluate(
                "e => { for (let p = e.parentElement; p; p = p.parentElement) {"
                " const o = getComputedStyle(p).overflowX; if (o === 'auto' || o === 'scroll') return true; } return false; }")
            if not wrapper:
                problems.append(f"{width}px: the table has no scroll container")
            for control in [page.locator("main select").first, page.locator("main select").last,
                            page.locator("input[type='date']").first, page.locator("input[type='date']").last,
                            page.get_by_role("button", name="Reset"),
                            page.locator("table tbody tr").first.locator("td").nth(1).get_by_role("link")]:
                control.scroll_into_view_if_needed()
                if not control.is_visible():
                    problems.append(f"{width}px: a control can't be reached")
            if page.locator("table tbody tr").count() == 0:
                problems.append(f"{width}px: no rows")
            page.close()
        browser.close()
        assert not problems, problems
