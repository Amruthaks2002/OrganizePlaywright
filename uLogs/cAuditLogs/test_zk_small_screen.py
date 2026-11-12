"""AL-038: Phone and tablet widths.

Steps:
1. Log in as admin with a 390 x 844 (phone) window, then a 768 x 1024 (tablet) window.
2. Open /audits.

Expected: the page doesn't scroll sideways (the table scrolls inside its own box), every filter, Reset All and the
View buttons can be reached, and rows are shown.
"""
import time

from playwright.sync_api import sync_playwright, expect
from utils.login_helper import login

BASE_URL = "https://organice.qc.iocod.com"
LOGS_URL = f"{BASE_URL}/audits"
SUBTITLE = "Track all system changes and user activities"
EMPTY_MESSAGE = "No audit logs found"


SIZES = [(390, 844), (768, 1024)]


def test_al_038_small_screen():
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
            wrapper = page.locator("table").first.evaluate(
                "e => { for (let p = e.parentElement; p; p = p.parentElement) {"
                " const o = getComputedStyle(p).overflowX; if (o === 'auto' || o === 'scroll') return true; } return false; }")
            if not wrapper:
                problems.append(f"{width}px: the table has no scroll container")
            for control in [page.locator("main select").first, page.locator("main select").nth(1),
                            page.locator("input[placeholder='Search by user...']"),
                            page.locator("input[type='date']").first, page.locator("input[type='date']").last,
                            page.get_by_role("button", name="Reset All"),
                            page.locator("table tbody tr").first.get_by_role("button", name="View")]:
                control.scroll_into_view_if_needed()
                if not control.is_visible():
                    problems.append(f"{width}px: a control can't be reached")
            if page.locator("table tbody tr").count() == 0:
                problems.append(f"{width}px: no rows")
            page.close()
        browser.close()
        assert not problems, problems
