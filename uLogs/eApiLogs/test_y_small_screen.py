"""API-025: Phone and tablet widths.

Steps:
1. Log in as admin with a 390 x 844 (phone) window, then a 768 x 1024 (tablet) window.
2. Open API Logs over all time.

Expected: the page doesn't scroll sideways (the table scrolls inside its own box), the search, both dropdowns, both
dates, Reset and the first time link can be reached, and rows are shown.
"""
import json
import time
from datetime import date
from urllib.parse import urlencode

from playwright.sync_api import sync_playwright, expect
from utils.login_helper import login

BASE_URL = "https://organice.qc.iocod.com"
LOGS_URL = f"{BASE_URL}/api-logs"
EMPTY_MESSAGE = "No API calls match these filters."
SEARCH = "input[placeholder='User name, email or reference']"


def page_props(page):
    """Props of a full page load (they go stale after in-page filtering, so only use them right after goto)."""
    return json.loads(page.locator("[data-page]").first.get_attribute("data-page"))["props"]


def props_at(page, url):
    page.goto(url)
    page.locator("main").first.wait_for(state="visible")
    time.sleep(1)
    return page_props(page)


def list_url(**filters):
    return f"{LOGS_URL}?{urlencode(filters)}"


def all_time():
    return {"start_date": "2000-01-01", "end_date": date.today().isoformat()}


SIZES = [(390, 844), (768, 1024)]


def test_api_025_small_screen():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        problems = []
        for width, height in SIZES:
            page = browser.new_page(viewport={"width": width, "height": height})
            login(page)
            props_at(page, list_url(**all_time()))
            if not page.evaluate("document.documentElement.scrollWidth <= window.innerWidth"):
                problems.append(f"{width}px: the page scrolls sideways")
            wrapper = page.locator("table").first.evaluate(
                "e => { for (let p = e.parentElement; p; p = p.parentElement) {"
                " const o = getComputedStyle(p).overflowX; if (o === 'auto' || o === 'scroll') return true; } return false; }")
            if not wrapper:
                problems.append(f"{width}px: the table has no scroll container")
            for control in [page.locator(SEARCH), page.locator("main select").first, page.locator("main select").last,
                            page.locator("input[type='date']").first, page.locator("input[type='date']").last,
                            page.get_by_role("button", name="Reset"),
                            page.locator("table tbody tr").first.locator("td").first.get_by_role("link")]:
                control.scroll_into_view_if_needed()
                if not control.is_visible():
                    problems.append(f"{width}px: a control can't be reached")
            if page.locator("table tbody tr").count() == 0:
                problems.append(f"{width}px: no rows")
            page.close()
        browser.close()
        assert not problems, problems
