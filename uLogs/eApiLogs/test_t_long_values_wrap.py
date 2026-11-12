"""API-020: Long values on the entry page.

Steps:
1. Log in as admin and open the newest ATS · User Sync and Open ATS (Sign-in) entries (long URLs, a long browser
   string and JSON payloads).

Expected: the page itself doesn't scroll sideways; long text wraps or scrolls inside its own box.
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


def test_api_020_long_values_wrap():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        login(page)

        problems = []
        for service in ["ats.user_sync", "ats.sso_launch"]:
            logs = props_at(page, list_url(service_name=service, start_date="2000-01-01",
                                           end_date=time.strftime("%Y-%m-%d")))["apiLogs"]["data"]
            if not logs:
                continue
            props_at(page, f"{LOGS_URL}/{logs[0]['id']}")
            page.get_by_role("link", name="← Back to API Logs").wait_for(state="visible")
            if not page.evaluate("document.documentElement.scrollWidth <= window.innerWidth"):
                problems.append(f"{service}: the page scrolls sideways")
            overflowing = page.evaluate("""() => [...document.querySelectorAll('main *')].filter(e => {
                const s = getComputedStyle(e);
                return e.scrollWidth > e.clientWidth + 1 && !['auto', 'scroll'].includes(s.overflowX)
                       && e.clientWidth > 0 && e.children.length === 0;
            }).map(e => e.tagName + ': ' + e.textContent.slice(0, 40))""")
            if overflowing:
                problems.append(f"{service}: text spills out of its box: {overflowing[:3]}")
        assert not problems, problems

        browser.close()
