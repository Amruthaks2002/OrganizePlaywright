"""WM-019: Work mode request actions are written to the audit log.

Steps (as admin, for the QA employee AutoUser_tNuUc, id 247, one-day Work From Home requests far in the future):
1. Apply request A, approve it, then cancel it.
2. Apply request B and reject it.
3. Apply request C and cancel it.
4. Open Work Mode Audit Logs filtered to the QA employee and today, and check the entries for each request.

Expected:
- A: Created, Approved, Cancelled. B: Created, Rejected. C: Created, Cancelled.
- Each entry is for the QA employee, Action By is Admin User, the time is within a few minutes of now, and the
  rows show up in the page table.
- Created says "Submitted a Work From Home work mode request for 1 day(s)."; Approved/Rejected say
  "... request approved/rejected by Admin User"; Cancelled says the request was cancelled.

Data left behind: work mode requests can't be deleted, so each run leaves 3 cancelled/rejected requests for the
QA employee (dates in 2027-2028). Nothing stays pending or approved: the finally block cancels anything still open.
"""
import json
import random
import time
from datetime import date, datetime, timedelta
from urllib.parse import unquote
from zoneinfo import ZoneInfo

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


IST = ZoneInfo("Asia/Kolkata")


def to_ist(created_at):
    return datetime.fromisoformat(created_at.replace("Z", "+00:00")).astimezone(IST)


def display_timestamp(created_at):
    """How the page shows a log time, e.g. 10 Nov, 2026, 03:02 PM (India time)."""
    return to_ist(created_at).strftime("%-d %b, %Y, %I:%M %p")


def displayed_date(timestamp):
    """The date part of a displayed timestamp."""
    return datetime.strptime(",".join(timestamp.split(",")[:2]).strip(), "%d %b, %Y").date()


QA_EMPLOYEE_ID = 247          # AutoUser_tNuUc, the dedicated QA employee (Morning policy)
WFH_ON_MORNING_POLICY = 1     # policy_work_mode_id of "Work From Home" on the Morning policy
QA_REASON = "QA work mode audit log"


def api_headers(page):
    # the meta csrf token goes stale after the SPA login, the XSRF cookie doesn't
    token = unquote(next(c["value"] for c in page.context.cookies() if c["name"] == "XSRF-TOKEN"))
    return {"X-XSRF-TOKEN": token, "X-Requested-With": "XMLHttpRequest", "Accept": "application/json"}


def free_weekdays(count):
    """Random weekdays far in the future, about five weeks apart, so the requests don't clash with each other or hit
    the 2-a-month Work From Home limit."""
    day = date(2027, 1, 4) + timedelta(days=random.randint(0, 500))
    days = []
    while len(days) < count:
        while day.weekday() >= 5:
            day += timedelta(days=1)
        days.append(day)
        day += timedelta(days=36)
    return days


def employee_logs_today(page):
    today = date.today().isoformat()
    return props_at(page, f"{LOGS_URL}?employee_id={QA_EMPLOYEE_ID}&from_date={today}&to_date={today}")["logs"]["data"]


def apply_work_mode(page, day, tag):
    """Applies a one-day Work From Home request for the QA employee as admin and returns its id, or None when the app
    refuses it. Work mode requests can't be deleted, only cancelled or rejected."""
    before = max([log["id"] for log in employee_logs_today(page)] or [0])
    page.request.post(f"{BASE_URL}/work-mode-application", headers=api_headers(page), max_redirects=0, multipart={
        "start_date": day.isoformat(), "end_date": day.isoformat(), "reason": f"{QA_REASON} {tag}",
        "policy_work_mode_id": str(WFH_ON_MORNING_POLICY), "day_type": "full", "start_half_session": "",
        "end_half_session": "", "supporting_document": "", "user_id": str(QA_EMPLOYEE_ID), "user_ids": "",
        "is_short_notice": "0"})
    created = [log for log in employee_logs_today(page) if log["id"] > before and log["action"] == "created"
               and (log.get("details") or {}).get("start_date") == day.isoformat()]
    return created[0]["work_mode_application_id"] if created else None


def set_work_mode_status(page, request_id, status, reason=QA_REASON):
    response = page.request.patch(f"{BASE_URL}/work-mode-application/{request_id}/status",
                                  data={"status": status, "action_reason": reason},
                                  headers=api_headers(page), max_redirects=0)
    assert response.status in (200, 302, 303), f"setting request {request_id} to {status} failed: {response.status}"


def cancel_work_mode(page, request_id, reason=QA_REASON):
    return page.request.fetch(f"{BASE_URL}/work-mode-application/{request_id}/cancel", method="DELETE",
                              data={"status": "cancel", "action_reason": reason},
                              headers=api_headers(page), max_redirects=0)


def logs_for_request(page, request_id):
    """The QA employee's audit log entries for one work mode request, oldest first."""
    return sorted([log for log in employee_logs_today(page) if log["work_mode_application_id"] == request_id],
                  key=lambda log: log["id"])


def test_wm_019_work_mode_lifecycle_logged():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        login(page)
        started = datetime.now(IST)
        plan = {"A": ["approved", "cancelled"], "B": ["rejected"], "C": ["cancelled"]}
        request_ids = {}
        problems = []
        try:
            for (key, steps), day in zip(plan.items(), free_weekdays(3)):
                request_id = apply_work_mode(page, day, f"WM-019 {key}")
                assert request_id, f"request {key} on {day} was refused"
                request_ids[key] = request_id
                for step in steps:
                    if step == "cancelled":
                        response = cancel_work_mode(page, request_id)
                        assert response.status in (200, 302, 303), f"cancelling {key} failed: {response.status}"
                    else:
                        set_work_mode_status(page, request_id, step)
                    time.sleep(1)

            for key, request_id in request_ids.items():
                logs = logs_for_request(page, request_id)
                shown = [r["description"] for r in table_rows(page)]
                actions = [log["action"] for log in logs]
                if actions != ["created"] + plan[key]:
                    problems.append(f"request {key} ({request_id}) logged {actions}")
                    continue
                for log in logs:
                    if log["user_id"] != QA_EMPLOYEE_ID:
                        problems.append(f"request {key}: {log['action']} is for user {log['user_id']}")
                    if not log["actor"] or log["actor"]["name"] != "Admin User":
                        problems.append(f"request {key}: {log['action']} action by {log['actor']}")
                    if abs((to_ist(log["created_at"]) - started).total_seconds()) > 600:
                        problems.append(f"request {key}: {log['action']} time {log['created_at']}")
                    if log["description"] not in shown:
                        problems.append(f"request {key}: {log['description']!r} is not in the table")
                    description = log["description"]
                    if log["action"] == "created" and description != "Submitted a Work From Home work mode request for 1 day(s).":
                        problems.append(f"request {key}: created says {description!r}")
                    if log["action"] in ("approved", "rejected") and \
                            f"Work From Home work mode request {log['action']} by Admin User" not in description:
                        problems.append(f"request {key}: {log['action']} says {description!r}")
                    if log["action"] == "cancelled" and "cancelled the Work From Home work mode request" not in description:
                        problems.append(f"request {key}: cancelled says {description!r}")
            assert not problems, problems
        finally:
            for key, request_id in request_ids.items():
                if "cancelled" not in plan[key] and "rejected" not in plan[key]:
                    cancel_work_mode(page, request_id)
            browser.close()
