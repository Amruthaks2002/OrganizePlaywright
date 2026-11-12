"""AL-028: The Changes column.

Steps:
1. Log in as admin and open Audit Logs over the year up to yesterday, pages 1-3, and once filtered to Deleted.
2. Compare every row's Changes text with the record behind it.

Expected: "No changes recorded" when nothing changed, otherwise "<n> field(s) <event>" where n is the number of
changed fields, with the right singular/plural ("1 field updated", "2 fields updated").

Known bug: one changed field is shown as "1 fields updated". This test fails until that's fixed.
"""
import json
import time
from datetime import date, timedelta
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


def expected_changes(audit):
    old = audit["old_values"] or {}
    new = audit["new_values"] or {}
    count = len(set(old) | set(new))
    if count == 0:
        return "No changes recorded"
    verb = audit["event"] if audit["event"] in ("created", "updated", "deleted") else "updated"
    return f"{count} field{'' if count == 1 else 's'} {verb}"


def test_al_028_changes_column_wording():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        login(page)
        start, end = wide_range()

        problems = []
        urls = [list_url(date_from=start, date_to=end, page=n) for n in (1, 2, 3)]
        urls += [list_url(date_from=start, date_to=end, event="deleted"), list_url(model="system_backup")]
        for url in urls:
            audits = props_at(page, url)["audits"]["data"]
            for audit, row in zip(audits, table_rows(page)):
                if row["changes"] != expected_changes(audit):
                    problems.append(f"{audit['id']} ({short(audit['model'])} {audit['event']}): "
                                    f"{row['changes']!r}, expected {expected_changes(audit)!r}")
        assert not problems, sorted(set(problems))[:15]

        browser.close()
