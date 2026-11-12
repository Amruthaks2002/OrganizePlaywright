"""LAL-028: Phone and tablet widths.

Steps:
1. Log in as admin with a 390 x 844 (phone) window, then a 768 x 1024 (tablet) window.
2. Open /leave-logs.

Expected: the page doesn't scroll sideways (the table scrolls inside its own container), every filter and the
Reset button can be reached, and rows are shown.
"""
import time

from playwright.sync_api import sync_playwright, expect
from utils.login_helper import login

BASE_URL = "https://organice.qc.iocod.com"
LOGS_URL = f"{BASE_URL}/leave-logs"
SUBTITLE = "A complete history of all leave-related actions."
EMPTY_MESSAGE = "No logs found for the selected criteria."


SIZES = [(390, 844), (768, 1024)]


def test_lal_028_small_screen():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        problems = []
        for width, height in SIZES:
            page = browser.new_page(viewport={"width": width, "height": height})
            login(page)
            page.goto(LOGS_URL)
            page.get_by_text(SUBTITLE).wait_for(state="visible")
            time.sleep(1)

            if not page.evaluate("document.documentElement.scrollWidth <= window.innerWidth"):
                problems.append(f"{width}px: the page scrolls sideways")
            wrapper = page.locator("table").evaluate(
                "e => { for (let p = e.parentElement; p; p = p.parentElement) {"
                " const o = getComputedStyle(p).overflowX; if (o === 'auto' || o === 'scroll') return true; } return false; }")
            if not wrapper:
                problems.append(f"{width}px: the table has no scroll container")
            for control in [page.locator("input[placeholder='Search by employee...']"),
                            page.locator("input[placeholder='Select action status...']"),
                            page.locator("input[type='date']").first, page.locator("input[type='date']").last,
                            page.locator("input[placeholder='Search text...']"), page.get_by_role("button", name="Reset")]:
                control.scroll_into_view_if_needed()
                if not control.is_visible():
                    problems.append(f"{width}px: a filter can't be reached")
            if page.locator("table tbody tr").count() == 0:
                problems.append(f"{width}px: no rows")
            page.close()
        browser.close()
        assert not problems, problems
