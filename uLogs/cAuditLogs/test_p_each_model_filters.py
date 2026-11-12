"""AL-016: Every Model option filters correctly.

Steps:
1. Open Audit Logs and set the dates to the year up to yesterday.
2. Select each Model option in turn.

Expected: the options are the models the server lists, and for each one every row (in the table and in the data
behind it) is of that model; when there are none the page says "No audit logs found".
"""
import json
import time
from datetime import date, timedelta
from urllib.parse import urlencode, urlparse

from playwright.sync_api import sync_playwright, expect
from utils.login_helper import login

BASE_URL = "https://organice.qc.iocod.com"
LOGS_URL = f"{BASE_URL}/audits"
SUBTITLE = "Track all system changes and user activities"
EMPTY_MESSAGE = "No audit logs found"


def open_audit_logs(page):
    """Logs in as admin and opens Logs > Audit Logs from the sidebar (Logs sits in the collapsed System section)."""
    login(page)
    page.get_by_test_id("sidebar-navigation").wait_for(state="visible")
    if not page.get_by_test_id("sidebar-parent-logs").is_visible():
        page.get_by_test_id("sidebar-section-system").dispatch_event("click")
    link = page.get_by_test_id("sidebar-child-audit-log")
    if not link.is_visible():
        page.get_by_test_id("sidebar-parent-logs").click()
    link.wait_for(state="visible")
    link.click()
    page.get_by_text(SUBTITLE).wait_for(state="visible")
    time.sleep(1)


def refresh(page, action):
    """Runs a filter action and returns the props of the list reload it triggers (filters are applied server side)."""
    with page.expect_response(lambda r: urlparse(r.url).path == "/audits" and r.request.method == "GET") as info:
        action()
    time.sleep(1)
    return info.value.json()["props"]


def page_props(page):
    """Props of a full page load (they go stale after in-page filtering, so only use them right after goto)."""
    return json.loads(page.locator("[data-page]").first.get_attribute("data-page"))["props"]


def props_at(page, url, wait_for=SUBTITLE):
    page.goto(url)
    page.get_by_text(wait_for).first.wait_for(state="visible")
    return page_props(page)


def list_url(**filters):
    return f"{LOGS_URL}?{urlencode(filters)}"


def table_rows(page):
    """Visible audit rows as dicts (the empty state has fewer cells and is skipped)."""
    rows = []
    for row in page.locator("table tbody tr").all():
        cells = row.locator("td")
        if cells.count() != 7:
            continue
        rows.append({
            "id": cells.nth(0).inner_text().strip(),
            "model": cells.nth(1).inner_text().strip(),
            "event": cells.nth(2).inner_text().strip(),
            "user": cells.nth(3).inner_text().strip(),
            "timestamp": cells.nth(4).inner_text().strip(),
            "changes": cells.nth(5).inner_text().strip(),
        })
    return rows


def short(model):
    return model.split("\\")[-1]


def total_records(page):
    return int(page.get_by_text("Total Records:").locator("xpath=following-sibling::span[1]").inner_text().strip())


def model_select(page):
    return page.locator("main select").first


def event_select(page):
    return page.locator("main select").nth(1)


def from_date(page):
    return page.locator("input[type='date']").first


def to_date(page):
    return page.locator("input[type='date']").last


def set_dates(page, start, end):
    """Sets the From/To boxes (in an order that never makes From later than To) and returns the last reload's props,
    or None when both already held those values."""
    props = None
    boxes = [(from_date(page), start), (to_date(page), end)]
    if to_date(page).input_value() and start > to_date(page).input_value():
        boxes.reverse()
    for box, value in boxes:
        if box.input_value() != value:
            props = refresh(page, lambda: box.fill(value))
    return props


def wide_range():
    """The year up to yesterday: ending yesterday so entries being written right now don't shift the rows."""
    today = date.today()
    return (today - timedelta(days=365)).isoformat(), (today - timedelta(days=1)).isoformat()


def test_al_016_each_model_filters():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        open_audit_logs(page)
        models = props_at(page, LOGS_URL)["models"]

        values = [o.get_attribute("value") for o in model_select(page).locator("option").all()]
        assert values[0] == "all" and sorted(values[1:]) == sorted(models), f"options {values} vs models {models}"
        set_dates(page, *wide_range())

        problems = []
        for model in models:
            props = refresh(page, lambda: model_select(page).select_option(value=model))
            got = {audit["model"] for audit in props["audits"]["data"]}
            if got - {model}:
                problems.append(f"{model}: data has {got}")
            rows = table_rows(page)
            if props["audits"]["total"] == 0:
                if not page.get_by_text(EMPTY_MESSAGE).is_visible():
                    problems.append(f"{model}: no rows but no empty message")
            elif any(row["model"] != short(model) for row in rows):
                problems.append(f"{model}: table shows {sorted({r['model'] for r in rows})}")
        assert not problems, problems

        browser.close()
