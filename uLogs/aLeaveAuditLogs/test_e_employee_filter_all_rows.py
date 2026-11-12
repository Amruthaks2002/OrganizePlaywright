"""LAL-004: The Employee filter keeps every row to the chosen employee.

Steps:
1. Log in as admin and open Leave Audit Logs over the year up to yesterday.
2. Pick the employee with the most rows in the first pages (that the dropdown offers).

Expected: there are results, and every row (in the table and in the data behind it) belongs to that employee,
not just the first one. The selected name is shown in the dropdown.
"""
import json
import time
from collections import Counter
from datetime import date, timedelta
from urllib.parse import parse_qs, urlparse

from playwright.sync_api import sync_playwright, expect
from utils.login_helper import login

BASE_URL = "https://organice.qc.iocod.com"
LOGS_URL = f"{BASE_URL}/leave-logs"
SUBTITLE = "A complete history of all leave-related actions."
EMPTY_MESSAGE = "No logs found for the selected criteria."


def refresh(page, action):
    """Runs a filter action and returns the props of the reload it triggers (filters are applied server side)."""
    with page.expect_response(lambda r: "/leave-logs" in r.url and r.request.method == "GET") as info:
        action()
    time.sleep(1)
    return info.value.json()["props"]


def page_props(page):
    """Props of a full page load (they go stale after in-page filtering, so only use them right after goto)."""
    return json.loads(page.locator("[data-page]").first.get_attribute("data-page"))["props"]


def props_at(page, url):
    page.goto(url)
    page.get_by_text(SUBTITLE).wait_for(state="visible")
    return page_props(page)


def table_rows(page):
    """Visible log rows as dicts (the empty-state row has a single cell and is skipped)."""
    rows = []
    for row in page.locator("table tbody tr").all():
        cells = row.locator("td")
        if cells.count() != 5:
            continue
        rows.append({
            "timestamp": cells.nth(0).inner_text().strip(),
            "employee": cells.nth(1).inner_text().strip(),
            "action_by": cells.nth(2).inner_text().strip(),
            "action": cells.nth(3).inner_text().strip(),
            "description": cells.nth(4).locator("p").first.inner_text().strip(),
            "details": cells.nth(4).inner_text().strip(),
        })
    return rows


def employee_box(page):
    return page.locator(".v-select").nth(0).locator("input.vs__search")


def search_response(text):
    """Matches the dropdown's /users/search call for this text."""
    return lambda r: "/users/search" in r.url and parse_qs(urlparse(r.url).query).get("query", [""])[0] == text


def offered(page, text):
    """Types into the Employee filter and returns the names it offers. The dropdown searches on the server, and the
    empty search fired on opening it can come back after the typed one, so wait for both."""
    box = employee_box(page)
    try:
        with page.expect_response(search_response(""), timeout=5000):
            page.locator(".v-select").nth(0).locator(".vs__dropdown-toggle").click()
    except Exception:
        pass  # the list was already loaded
    with page.expect_response(search_response(text), timeout=15000):
        box.fill(text)
    time.sleep(1)
    if page.get_by_text("No employees found").is_visible():
        return []
    return [o.strip() for o in page.get_by_role("option").all_inner_texts()]


def pick_employee(page, name):
    offered(page, name)
    return refresh(page, lambda: page.get_by_role("option", name=name, exact=True).click())


def pick_first_selectable(page, names):
    """Selects the first of these names that the Employee dropdown offers (it doesn't offer every employee who has
    logs, e.g. relieved ones) and that has rows under the other filters; returns (name, props)."""
    for name in names:
        if name in offered(page, name):
            props = refresh(page, lambda: page.get_by_role("option", name=name, exact=True).click())
            if props["logs"]["total"] > 0:
                return name, props
    raise AssertionError(f"none of {names} can be picked in the Employee filter with rows to show")


def wide_range():
    """The year up to yesterday: wide enough to have logs of most kinds, and ending yesterday so logs being written
    right now (by other tests or users) don't shift the rows while a test reads them."""
    today = date.today()
    return (today - timedelta(days=365)).isoformat(), (today - timedelta(days=1)).isoformat()


def employees_with_logs(page, start, end):
    """Employees with logs in the range, most rows first. Samples the first page of several actions, because one busy
    QA account (AutoUser_tNuUc, used by the payroll tests) can fill every page of the unfiltered list. Leaves the
    page showing the range with no other filter."""
    counts = Counter()
    for status in ["", "created", "approved", "rejected", "cancelled", "updated"]:
        extra = f"&status={status}" if status else ""
        props = props_at(page, f"{LOGS_URL}?from_date={start}&to_date={end}{extra}")
        counts.update(log["user"]["name"] for log in props["logs"]["data"])
    props_at(page, f"{LOGS_URL}?from_date={start}&to_date={end}")
    return [name for name, _ in counts.most_common()]


def test_lal_004_employee_filter_all_rows():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        login(page)

        names = employees_with_logs(page, *wide_range())
        employee, props = pick_first_selectable(page, names)
        assert props["logs"]["total"] > 0
        assert {log["user"]["name"] for log in props["logs"]["data"]} == {employee}

        rows = table_rows(page)
        assert rows, "no rows after filtering"
        assert all(row["employee"] == employee for row in rows), [r["employee"] for r in rows]
        expect(page.locator(".vs__selected").first).to_have_text(employee)

        browser.close()
