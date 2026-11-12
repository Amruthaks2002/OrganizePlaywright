"""WM-021: The longest description is shown in full and wraps inside its column.

Steps:
1. Log in as admin and open Work Mode Audit Logs over the year up to yesterday, pages 1-5.
2. Take the row with the longest description and open the page it is on.

Expected: the whole description is in the cell, nothing is clipped or hidden (the text wraps instead of
overflowing), the Description column stays within its max width (28rem) and the page doesn't scroll sideways.
"""
import json
import time
from datetime import date, timedelta

from playwright.sync_api import sync_playwright, expect
from utils.login_helper import login

BASE_URL = "https://organice.qc.iocod.com"
LOGS_URL = f"{BASE_URL}/work-mode-logs"
SUBTITLE = "A complete history of all work mode-related actions."
EMPTY_MESSAGE = "No logs found for the selected criteria."


def page_props(page):
    """Props of a full page load (they go stale after in-page filtering, so only use them right after goto)."""
    props = json.loads(page.locator("[data-page]").first.get_attribute("data-page"))["props"]
    props["filters"] = props["filters"] or {}  # the app sends [] when nothing is filtered
    return props


def props_at(page, url):
    page.goto(url)
    page.get_by_text(SUBTITLE).wait_for(state="visible")
    return page_props(page)


def wide_range():
    """The year up to yesterday: wide enough to have logs of most kinds, and ending yesterday so logs being written
    right now (by other tests or users) don't shift the rows while a test reads them."""
    today = date.today()
    return (today - timedelta(days=365)).isoformat(), (today - timedelta(days=1)).isoformat()


def test_wm_021_long_description_wraps():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        login(page)
        start, end = wide_range()

        longest, longest_page, longest_row = None, 1, 0
        for number in range(1, 6):
            props = props_at(page, f"{LOGS_URL}?from_date={start}&to_date={end}&page={number}")
            for index, log in enumerate(props["logs"]["data"]):
                if longest is None or len(log["description"]) > len(longest["description"]):
                    longest, longest_page, longest_row = log, number, index
            if number >= props["logs"]["last_page"]:
                break
        assert longest, "no logs in the year up to yesterday"
        props = props_at(page, f"{LOGS_URL}?from_date={start}&to_date={end}&page={longest_page}")
        assert props["logs"]["data"][longest_row]["id"] == longest["id"], "the rows moved while reading"

        description = longest["description"]
        cell = page.locator("table tbody tr").nth(longest_row).locator("td").nth(4)
        expect(cell).to_be_visible()
        text = cell.locator("p").first
        assert text.inner_text().strip() == description.strip(), "the description is cut short"
        sizes = text.evaluate("e => ({sw: e.scrollWidth, cw: e.clientWidth, sh: e.scrollHeight, ch: e.clientHeight})")
        assert sizes["sw"] <= sizes["cw"] and sizes["sh"] <= sizes["ch"], f"text is clipped: {sizes}"
        assert cell.evaluate("e => e.getBoundingClientRect().width") <= 448 + 1, "the column is wider than 28rem"
        assert page.evaluate("document.documentElement.scrollWidth <= window.innerWidth"), "the page scrolls sideways"

        browser.close()
