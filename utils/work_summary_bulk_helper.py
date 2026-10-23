"""Helpers for the Work Summary bulk operations tests (fWorkManagement/work_summary/gBulkOperations).

Bulk actions work on the rows ticked in the Regular Hours / Comp Hours tables: a selection dock appears at the
bottom with Approve (n) / Reject (n) (Comp Hours only) and Delete (n), and each sends
POST /hours/bulk-{approve,reject,delete} {time_log_ids: [...]}.

Test entries get short descriptions ('QA WS a1b2c3-01') because the table cuts descriptions after 15 characters,
so every entry can be told apart by its row. Approving can never be undone (see work_summary_helper), so anything
that could approve for real runs only as the throwaway comp user."""
import json
import re
from datetime import date, timedelta
from urllib.parse import unquote

import pytest
from playwright.sync_api import Page, expect
from utils.work_summary_helper import (HOURS_URL, DAILY_CAP, open_hours, open_tab, from_date, to_date, wait_for_logs,
                                       pick_employee, status_select, rows, page_props, logs_api, delete_log_api,
                                       comp_user_credentials, open_browser_with_login, today, settle, main_content,
                                       summary_card, card_number, COMP_USER_ENV, BASE_URL, BADGES)
from utils.onboarding_helper import unique_tag, login_as

BULK_URL = f"{HOURS_URL}/bulk-"
NOTIFICATIONS_URL = f"{BASE_URL}/notifications"
PROJECT_ID = 33  # project Beta
SEARCH_DAYS = 200
SELECT_ALL_LABEL = "Select all time logs on this page"

# server messages (flash success / error, or 422 JSON for validation)
EMPTY_ERROR = "Please select at least one time log."
MISSING_ERROR = "One of the selected time logs no longer exists."
NOT_INTEGER_ERROR = "The time_log_ids.0 field must be an integer."
DUPLICATE_ERROR = "The time_log_ids.0 field has a duplicate value."
NONE_DELETED = "None of the selected time logs could be deleted."
NONE_REJECTED = "None of the selected requests could be rejected."
NONE_APPROVED = "None of the selected requests could be approved."
REJECTED_NOTIFICATION = ("Compensatory Work Rejected", "compensatory_work_rejected")

# every log a bulk test creates, so the session can mark the notifications they caused as read (see conftest)
CREATED_LOG_IDS = set()


def deleted_msg(n):
    return f"{n} time {'log' if n == 1 else 'logs'} deleted."


def rejected_msg(n):
    return f"{n} comp-off {'request' if n == 1 else 'requests'} rejected."


def approved_msg(n):
    return f"{n} comp-off {'request' if n == 1 else 'requests'} approved."


def skipped_msg(n):
    return f"Skipped {n} (already decided or not permitted)."


# ---------- descriptions ----------

def bulk_prefix():
    """'QA WS a1b2c3' - with '-01', '-02'... it stays within the 15 characters the table shows."""
    return f"QA WS {unique_tag()[:6]}"


def entry_desc(prefix, i):
    return f"{prefix}-{i:02d}"


# ---------- server data ----------

def _xsrf(page: Page):
    return unquote(next(c["value"] for c in page.context.cookies() if c["name"] == "XSRF-TOKEN"))


def me(page: Page):
    return page_props(page)["auth"]["user"]


def own_hours_on(page: Page, day, user_id):
    return sum(float(log["hours_worked"])
               for comp_filter in ("regular", "compensatory")
               for log in logs_api(page, comp_filter, start=day, end=day, employee_id=user_id)["timeLogs"]["data"])


def find_prefixed(page: Page, prefix, days=SEARCH_DAYS, **extra):
    """Every log (regular or comp, any page) the signed-in user can see whose description starts with `prefix`,
    sorted by description."""
    found = []
    start = today() - timedelta(days=days)
    for comp_filter in ("regular", "compensatory"):
        page_no, last = 1, 1
        while page_no <= last:
            data = logs_api(page, comp_filter, start=start, page_no=page_no, **extra)["timeLogs"]
            found += [log for log in data["data"] if (log["description"] or "").startswith(prefix)]
            last = data["last_page"]
            page_no += 1
    return sorted(found, key=lambda log: log["description"])


def _create_log(page: Page, desc, day, hours, project_id=PROJECT_ID):
    return page.request.post(HOURS_URL, form={"project_id": str(project_id), "work_date": day.isoformat(),
                                              "hours_worked": str(hours), "description": desc},
                             headers={"X-XSRF-TOKEN": _xsrf(page)}, max_redirects=0).status


def create_logs(page: Page, prefix, count, comp=True, hours=1, start_index=1, max_days=SEARCH_DAYS):
    """Logs `count` entries for the signed-in user ('<prefix>-01', '-02'...), on weekend days for comp entries or
    working days for regular ones, going back from today and filling each day up to the daily cap. The server refuses
    days the user is on leave, and hours on a holiday become a comp request instead, so those days are skipped.
    Returns the new logs sorted by description."""
    if page.url != HOURS_URL:
        open_hours(page)
    user = me(page)
    weekends = page_props(page)["weekends"]
    made, i = [], start_index
    day = today() - timedelta(days=1) if comp else today()
    for _ in range(max_days):
        if len(made) == count:
            break
        if (day.isoweekday() in weekends) == comp:
            room = int((DAILY_CAP - own_hours_on(page, day, user["id"])) // hours)
            for _ in range(min(room, count - len(made))):
                desc = entry_desc(prefix, i)
                _create_log(page, desc, day, hours)
                logs = [log for comp_filter in ("regular", "compensatory")
                        for log in logs_api(page, comp_filter, start=day, end=day, employee_id=user["id"])["timeLogs"]["data"]
                        if log["description"] == desc]
                if not logs:
                    break  # refused (e.g. a leave day): try an earlier day
                [log] = logs
                CREATED_LOG_IDS.add(log["id"])
                if log["is_weekend_or_holiday"] != comp:  # a holiday
                    delete_log_api(page, log["id"])
                    break
                made.append(log)
                i += 1
        day -= timedelta(days=1)
    assert len(made) == count, f"could only log {len(made)} of {count} {'comp' if comp else 'regular'} entries"
    return sorted(made, key=lambda log: log["description"])


def cleanup_prefixed(admin: Page, prefix, days=SEARCH_DAYS):
    """Deletes every log starting with `prefix`, whoever it belongs to (used in finally). Needs an admin page:
    only an admin may delete rejected entries. Approved entries can't be deleted and stay."""
    for log in find_prefixed(admin, prefix, days):
        if log["comp_off_status"] != "approved":
            delete_log_api(admin, log["id"])
    left = [log for log in find_prefixed(admin, prefix, days) if log["comp_off_status"] != "approved"]
    assert not left, f"could not clean up {[log['description'] for log in left]}"


def statuses(page: Page, prefix, **extra):
    """{description: comp_off_status} of the logs starting with `prefix`."""
    return {log["description"]: log["comp_off_status"] for log in find_prefixed(page, prefix, **extra)}


def approved_row(page: Page):
    """An approved comp entry on the current page, logged before (approved entries can't be made and removed by a
    test). It's only ever ticked: the page leaves approved entries out of every bulk action."""
    found = rows(page).filter(has_text=BADGES["approved"])
    if not found.count():
        pytest.skip("no approved comp entry in range to tick")
    return found.first


def pending_hours(page: Page):
    """'Total Hours' on the Pending Comp Hours card (shown once an employee is picked)."""
    return card_number(summary_card(page, "Pending Comp Hours"), "Total Hours")


# ---------- API ----------

def bulk_api(page: Page, action, ids, json_errors=True, xsrf=True):
    """POST /hours/bulk-<action>. Validation errors come back as 422 JSON when asked for it; otherwise the server
    redirects back (302) and the outcome is the flash message on the next page load.
    Returns (status, body): the parsed 422/4xx JSON, the flash ({'success': ...} / {'error': ...}) after a 302,
    or the raw text."""
    headers = {}
    if xsrf:
        headers["X-XSRF-TOKEN"] = _xsrf(page)
    if json_errors:
        headers["Accept"] = "application/json"
    response = page.request.post(f"{BULK_URL}{action}", data={"time_log_ids": ids}, headers=headers, max_redirects=0)
    if response.status == 302:
        page.goto(HOURS_URL)
        settle(page)
        return 302, {k: v for k, v in page_props(page)["flash"].items() if v and k in ("success", "error")}
    try:
        return response.status, response.json()
    except Exception:
        return response.status, response.text()


# ---------- page ----------

def show_entries(page: Page, tab, start, end=None, employee=None, status=None):
    """Opens Work Summary on `tab` showing `start`..`end` (end defaults to today), narrowed to an employee
    and/or comp status. Returns the logs JSON of the last refetch."""
    open_hours(page)
    data = open_tab(page, tab)
    if from_date(page).input_value() != start.isoformat():
        data = wait_for_logs(page, lambda: from_date(page).fill(start.isoformat()))
    if end and to_date(page).input_value() != end.isoformat():
        data = wait_for_logs(page, lambda: to_date(page).fill(end.isoformat()))
    if employee:
        data = wait_for_logs(page, lambda: pick_employee(page, employee))
    if status:
        data = wait_for_logs(page, lambda: status_select(page).select_option(status))
    return data


def earliest(logs):
    return min(date.fromisoformat(log["work_date"][:10]) for log in logs)


def latest(logs):
    return max(date.fromisoformat(log["work_date"][:10]) for log in logs)


def entry_row(page: Page, desc):
    return rows(page).filter(has_text=desc)


def row_checkbox(tr):
    return tr.locator("td").first.locator("input[type=checkbox]")


def header_checkbox(page: Page):
    return main_content(page).get_by_label(SELECT_ALL_LABEL)


def tick(page: Page, *descs):
    for desc in descs:
        row_checkbox(entry_row(page, desc)).check()


def untick(page: Page, *descs):
    for desc in descs:
        row_checkbox(entry_row(page, desc)).uncheck()


def dock(page: Page):
    return page.get_by_test_id("selection-dock")


def dock_toolbar(page: Page):
    return dock(page).get_by_role("toolbar")


def dock_button(page: Page, action):
    """Approve / Reject / Delete - their label carries the count: 'Delete (2)'."""
    return dock(page).get_by_role("button", name=re.compile(rf"^\s*{action} \(\d+\)\s*$"))


def dock_clear(page: Page):
    return page.get_by_test_id("selection-dock-clear")


def expect_dock(page: Page, selected, **buttons):
    """The dock shows `selected` time logs and, for each action given, that count (enabled only when > 0).
    An action given as None must not be in the dock at all."""
    expect(dock(page)).to_be_visible()
    noun = "time log" if selected == 1 else "time logs"
    # the count is a badge of its own, then '<noun> selected'
    expect(dock_toolbar(page).locator("span").first).to_have_text(str(selected))
    expect(dock_toolbar(page).locator("span").nth(1)).to_have_text(f"{noun} selected")
    expect(dock_toolbar(page)).to_have_attribute("aria-label", f"Actions for {selected} selected {noun}")
    for action, count in buttons.items():
        button = dock_button(page, action.capitalize())
        if count is None:
            expect(button).to_have_count(0)
            continue
        expect(button).to_have_text(f"{action.capitalize()} ({count})")
        if count:
            expect(button).to_be_enabled()
        else:
            expect(button).to_be_disabled()


def confirm_dialog(page: Page):
    return page.get_by_test_id("confirm-dialog").last


def expect_confirm(page: Page, title, message, confirm_text, danger=None):
    """The open confirm dialog's texts; `danger` checks the confirm button is red (True) or indigo (False)."""
    dialog = confirm_dialog(page)
    expect(dialog.locator("#confirm-dialog-title")).to_have_text(title)
    expect(dialog.locator("#confirm-dialog-message")).to_have_text(message)
    confirm = dialog.get_by_test_id("confirm-dialog-confirm")
    expect(confirm).to_have_text(confirm_text)
    if danger is not None:
        expect(confirm).to_have_class(re.compile(r"\bbg-red-600\b" if danger else r"\bbg-indigo-600\b"))
    return dialog


def watch_bulk(page: Page):
    """Records every bulk POST the page sends from now on (a list of (action, time_log_ids))."""
    sent = []

    def record(request):
        if request.method == "POST" and request.url.startswith(BULK_URL):
            sent.append((request.url[len(BULK_URL):], json.loads(request.post_data or "{}").get("time_log_ids")))
    page.on("request", record)
    return sent


def open_bulk(page: Page, action):
    """Clicks a dock action (Approve / Reject / Delete) and returns its confirm dialog."""
    dock_button(page, action).click()
    dialog = confirm_dialog(page)
    expect(dialog).to_be_visible()
    return dialog


def confirm_bulk(page: Page, action):
    """Confirms the open bulk dialog and returns the time_log_ids the page sent."""
    with page.expect_request(lambda r: r.url == f"{BULK_URL}{action.lower()}" and r.method == "POST") as request:
        confirm_dialog(page).get_by_test_id("confirm-dialog-confirm").click()
    expect(page.get_by_test_id("confirm-dialog")).to_have_count(0)
    return json.loads(request.value.post_data or "{}")["time_log_ids"]


def run_bulk(page: Page, action):
    """Clicks a dock action, confirms it, and returns the time_log_ids the page sent."""
    open_bulk(page, action)
    return confirm_bulk(page, action)


def cancel_bulk(page: Page):
    confirm_dialog(page).get_by_test_id("confirm-dialog-cancel").click()
    expect(page.get_by_test_id("confirm-dialog")).to_have_count(0)


# ---------- the throwaway comp user (approving for real) ----------

def comp_user_or_skip():
    credentials = comp_user_credentials()
    if not credentials:
        pytest.skip(f"set {' / '.join(COMP_USER_ENV)} to a throwaway user: approving can't be undone")
    return credentials


def open_comp_user(p, credentials):
    """Signs in as the throwaway comp user. Get `credentials` from comp_user_or_skip() before starting Playwright:
    skipping once Playwright is running leaves its startup task pending ('Task was destroyed but it is pending!')."""
    return open_browser_with_login(p, *credentials)


# ---------- notifications ----------

def _inertia_version(page: Page):
    return json.loads(page.locator("[data-page]").first.get_attribute("data-page") or "{}").get("version") or ""


def mark_notifications_read(page: Page, log_ids, pages=3):
    """Marks the signed-in user's unread notifications about `log_ids` as read, so the tests leave everyone's
    unread count as it was. Notifications can't be deleted."""
    version = _inertia_version(page)
    for page_no in range(1, pages + 1):
        data = page.request.get(f"{NOTIFICATIONS_URL}?page={page_no}",
                                headers={"X-Inertia": "true", "X-Inertia-Version": version}).json()["props"]["notifications"]
        for n in data["data"]:
            if n["read_at"] is None and n["data"].get("time_log_id") in log_ids:
                page.request.post(f"{NOTIFICATIONS_URL}/{n['id']}/read", headers={"X-XSRF-TOKEN": _xsrf(page)})
        if page_no >= data["last_page"]:
            break


def notifications_for(page: Page, log_id):
    version = _inertia_version(page)
    data = page.request.get(f"{NOTIFICATIONS_URL}?page=1",
                            headers={"X-Inertia": "true", "X-Inertia-Version": version}).json()["props"]["notifications"]
    return [n for n in data["data"] if n["data"].get("time_log_id") == log_id]


def sign_in_page(browser, role):
    page = browser.new_context(viewport={"width": 1600, "height": 900}).new_page()
    login_as(page, role)
    return page
