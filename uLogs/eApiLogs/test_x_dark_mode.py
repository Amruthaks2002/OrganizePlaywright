"""API-024: Light and dark mode.

Steps:
1. Open API Logs over all time (light mode) and note the colours of the table header, a row, a filter and the
   heading.
2. Switch the theme with the theme toggle, then switch it back.

Expected: dark mode puts the "dark" class on the page and all of those colours change; switching back restores
them.
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


def colours(page):
    def css(locator, prop):
        return locator.evaluate(f"e => getComputedStyle(e).{prop}")
    return {
        "header": css(page.locator("table thead th").first, "color"),
        "row": css(page.locator("table tbody tr td").nth(1), "color"),
        "filter": css(page.locator("input[type='date']").first, "backgroundColor"),
        "heading": css(page.get_by_role("heading", name="API Logs"), "color"),
    }


def is_dark(page):
    return "dark" in (page.locator("html").get_attribute("class") or "").split()


def test_api_024_dark_mode():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        login(page)
        props_at(page, list_url(**all_time()))
        toggle = page.get_by_test_id("theme-toggle-button")
        try:
            if is_dark(page):
                toggle.click()
                time.sleep(1)
            light = colours(page)
            toggle.click()
            time.sleep(1)
            assert is_dark(page)
            dark = colours(page)
            same = [key for key in light if light[key] == dark[key]]
            assert not same, f"unchanged in dark mode: {same} ({dark})"
            toggle.click()
            time.sleep(1)
            assert not is_dark(page)
            assert colours(page) == light
        finally:
            browser.close()
