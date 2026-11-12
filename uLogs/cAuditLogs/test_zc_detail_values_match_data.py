"""AL-029: The Audit History page matches the records behind it.

Steps:
1. Open Audit Logs filtered to updated LeaveApplication records over the year up to yesterday and click View on
   the first row with changes. Then do the same for a created and a deleted record.
2. Compare the page with the entity's audit records.

Expected:
- The header shows "<Model> #<id>" and the full model class.
- The summary table has one row per record, with Date / User / Event plus one column per changed field.
- "Showing N audit record(s)" matches the number of report cards and records.
- Each of the first report cards shows its time, user and event, and one line per changed field with the old and
  new value ("-" when empty).
"""
import json
import re
import time
from datetime import date, datetime, timedelta, timezone
from urllib.parse import urlencode
from zoneinfo import ZoneInfo

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


def wide_range():
    """The year up to yesterday: ending yesterday so entries being written right now don't shift the rows."""
    today = date.today()
    return (today - timedelta(days=365)).isoformat(), (today - timedelta(days=1)).isoformat()


IST = ZoneInfo("Asia/Kolkata")


def to_ist(created_at):
    """Audit times come as '2026-11-11T06:33:43.793000Z' (list) or '2026-11-11 06:33:43' (detail), both UTC."""
    moment = datetime.fromisoformat(created_at.replace("Z", "").replace(" ", "T"))
    return moment.replace(tzinfo=timezone.utc).astimezone(IST)


def display_timestamp(created_at):
    """How the page shows a time, e.g. 11 Nov, 2026, 03:50 PM (India time)."""
    return to_ist(created_at).strftime("%-d %b, %Y, %I:%M %p")


def displayed_date(timestamp):
    return datetime.strptime(",".join(timestamp.split(",")[:2]).strip(), "%d %b, %Y").date()


def open_detail(page, row_index=0):
    """Clicks View on a row and returns the props of the Audit History it loads."""
    with page.expect_response(lambda r: "/audits/entity" in r.url) as info:
        page.locator("table tbody tr").nth(row_index).get_by_role("button", name="View").click()
    page.get_by_role("heading", name="Audit History").wait_for(state="visible")
    time.sleep(1)
    return info.value.json()["props"]


def report_cards(page):
    return page.locator("div.rounded-lg.border.overflow-hidden")


def shown(value):
    """How the detail page shows a stored value: '-' for empty."""
    return "-" if value is None or value == "" else str(value)


def check_detail(page, entity_props, problems, label):
    entity = entity_props["entity"]
    audits = entity_props["audits"]
    if page.get_by_text(f"{entity['short_type']} #{entity['auditable_id']}", exact=True).count() == 0:
        problems.append(f"{label}: header doesn't say {entity['short_type']} #{entity['auditable_id']}")
    if page.get_by_text(entity["auditable_type"], exact=True).count() == 0:
        problems.append(f"{label}: full model name missing")

    summary = page.locator("main table").first
    headers = [h.strip().upper() for h in summary.locator("thead th").all_inner_texts()]
    expected_headers = ["DATE", "USER", "EVENT"] + [c.replace("_", " ").upper() for c in entity_props["columns"]]
    if headers != expected_headers:
        problems.append(f"{label}: summary columns {headers}, expected {expected_headers}")
    if summary.locator("tbody tr").count() != len(audits):
        problems.append(f"{label}: summary has {summary.locator('tbody tr').count()} rows for {len(audits)} records")

    showing = int(re.search(r"Showing (\d+)", page.get_by_text(re.compile(r"Showing \d+ audit record")).inner_text()).group(1))
    if not showing == report_cards(page).count() == len(audits):
        problems.append(f"{label}: Showing {showing}, {report_cards(page).count()} cards, {len(audits)} records")

    for index, audit in enumerate(audits[:3]):
        card = report_cards(page).nth(index)
        text = card.inner_text()
        for part in [f"Audit Report {index + 1}", display_timestamp(audit["created_at"]), audit["user"] or "System", audit["event"]]:
            if part not in text:
                problems.append(f"{label}: card {index + 1} is missing {part!r}")
        lines = [[c.strip() for c in row.locator("td").all_inner_texts()] for row in card.locator("tbody tr").all()]
        keys = audit["changed_keys"]
        if not keys:
            if "No field-level differences for this record." not in text:
                problems.append(f"{label}: card {index + 1} has no changes but no 'No field-level differences'")
            continue
        old, new = audit["old_values"] or {}, audit["new_values"] or {}
        expected = [[key, shown(old.get(key)), shown(new.get(key))] for key in keys]
        if lines != expected:
            problems.append(f"{label}: card {index + 1} shows {lines}, expected {expected}")


def test_al_029_detail_values_match_data():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        login(page)
        start, end = wide_range()
        problems = []
        for event in ["updated", "created", "deleted"]:
            props = props_at(page, list_url(model="App\\Models\\LeaveApplication", event=event, date_from=start, date_to=end))
            audits = props["audits"]["data"]
            index = next((i for i, a in enumerate(audits) if a["old_values"] or a["new_values"]), None)
            assert index is not None, f"no {event} LeaveApplication record with changes on page 1"
            check_detail(page, open_detail(page, index), problems, event)
        assert not problems, problems

        browser.close()
