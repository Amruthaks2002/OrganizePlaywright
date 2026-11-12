"""AL-018: The Event Type dropdown offers every event that appears in the logs.

Steps:
1. Log in as admin and load Audit Logs filtered to each model in turn.
2. Collect the events on the first page of each model.
3. Compare them with the Event Type options.

Expected: every event that appears can be filtered by.

Known bug: backup records use events such as "Backup.Downloaded", which the Event Type dropdown (All Events,
Created, Updated, Deleted) can't select. This test fails until that's fixed.
"""
import json
import time
from urllib.parse import urlencode

from playwright.sync_api import sync_playwright, expect
from utils.login_helper import login

BASE_URL = "https://organice.qc.iocod.com"
LOGS_URL = f"{BASE_URL}/audits"
SUBTITLE = "Track all system changes and user activities"
EMPTY_MESSAGE = "No audit logs found"


def page_props(page):
    """Props of a full page load (they go stale after in-page filtering, so only use them right after goto)."""
    return json.loads(page.locator("[data-page]").first.get_attribute("data-page"))["props"]


def props_at(page, url, wait_for=SUBTITLE):
    page.goto(url)
    page.get_by_text(wait_for).first.wait_for(state="visible")
    return page_props(page)


def list_url(**filters):
    return f"{LOGS_URL}?{urlencode(filters)}"


def model_select(page):
    return page.locator("main select").first


def event_select(page):
    return page.locator("main select").nth(1)


def test_al_018_event_options_cover_data():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        login(page)

        props = props_at(page, LOGS_URL)
        options = {o.get_attribute("value") for o in event_select(page).locator("option").all()} - {"all"}
        seen = {}
        for model in props["models"]:
            for audit in props_at(page, list_url(model=model))["audits"]["data"]:
                seen.setdefault(audit["event"], model)
        missing = {event: model for event, model in seen.items() if event not in options}
        assert not missing, f"events that can't be filtered (event: model): {missing}; options are {sorted(options)}"

        browser.close()
