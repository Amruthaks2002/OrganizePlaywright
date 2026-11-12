"""WM-010: Action badge labels and colours.

Steps:
1. Log in as admin.
2. For each action, open Work Mode Audit Logs filtered to that action over the year up to yesterday.

Expected:
- The actions use the agreed colours: Created blue, Approved green, Rejected red, Cancelled yellow,
  Updated blue, Deleted red.
- Every badge shows the action's label and is drawn in that action's colour (bg-<colour>-100).
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


CORE_COLOURS = {"created": "blue", "approved": "green", "rejected": "red", "cancelled": "yellow", "updated": "blue",
                "deleted": "red"}


def test_wm_010_action_badge_colours():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        login(page)
        start, end = wide_range()

        options = props_at(page, LOGS_URL)["actionOptions"]
        colours = {o["value"]: o["color"] for o in options}
        for action, colour in CORE_COLOURS.items():
            assert colours.get(action) == colour, f"{action} is {colours.get(action)}, expected {colour}"

        problems = []
        checked = 0
        for option in options:
            props = props_at(page, f"{LOGS_URL}?status={option['value']}&from_date={start}&to_date={end}")
            badges = page.locator("table tbody tr td:nth-child(4) span")
            for i in range(badges.count()):
                checked += 1
                badge = badges.nth(i)
                text = badge.inner_text().strip()
                css = (badge.get_attribute("class") or "").split()
                if text != option["label"]:
                    problems.append(f"{option['value']}: badge says {text}")
                if f"bg-{option['color']}-100" not in css:
                    problems.append(f"{option['label']}: badge class {css} is not {option['color']}")
        assert checked, "no badges found at all"
        assert not problems, sorted(set(problems))

        browser.close()
