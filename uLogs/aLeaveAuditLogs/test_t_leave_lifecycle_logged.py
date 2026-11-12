"""LAL-019: Leave actions are written to the audit log.

Steps (as admin, for the QA employee AutoUser_tNuUc, id 247, using one-day LOP leaves far in the future):
1. Apply leave A, approve it, then delete it.
2. Apply leave B, reject it, then delete it.
3. Apply leave C, cancel it, then delete it.
4. Open Leave Audit Logs filtered to the QA employee and today, and check the entries for each leave.

Expected:
- A: Created, Approved, Deleted. B: Created, Rejected, Deleted. C: Created, Cancelled, Deleted.
- Each entry is for the QA employee, Action By is Admin User, the time is within a few minutes of now.
- Created says "Submitted a loss of pay leave request for 1 day(s)."; Approved/Rejected name the action and the
  admin; Deleted says the leave was deleted by Admin User.
- The rows show up in the page table too.

Cleanup: every leave is deleted in a finally block (deleting gives the day back to the balance). The audit log
entries themselves are permanent by design.
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
LOGS_URL = f"{BASE_URL}/leave-logs"
SUBTITLE = "A complete history of all leave-related actions."
EMPTY_MESSAGE = "No logs found for the selected criteria."


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


IST = ZoneInfo("Asia/Kolkata")


def to_ist(created_at):
    return datetime.fromisoformat(created_at.replace("Z", "+00:00")).astimezone(IST)


def display_timestamp(created_at):
    """How the page shows a log time, e.g. 10 Nov, 2026, 03:02 PM (India time)."""
    return to_ist(created_at).strftime("%-d %b, %Y, %I:%M %p")


def displayed_date(timestamp):
    """The date part of a displayed timestamp."""
    return datetime.strptime(",".join(timestamp.split(",")[:2]).strip(), "%d %b, %Y").date()


QA_EMPLOYEE_ID = 247          # AutoUser_tNuUc, the dedicated QA employee (Morning leave policy)
LOP_LEAVE = 57                # "Loss of pay Leave" on the Morning policy
QA_REASON = "QA leave audit log"


def api_headers(page):
    # the meta csrf token goes stale after the SPA login, the XSRF cookie doesn't
    token = unquote(next(c["value"] for c in page.context.cookies() if c["name"] == "XSRF-TOKEN"))
    return {"X-XSRF-TOKEN": token, "X-Requested-With": "XMLHttpRequest", "Accept": "application/json"}


def free_weekdays(count):
    """Random weekdays well in the future so the QA leaves don't clash with each other or with payroll tests."""
    day = date(2027, 6, 1) + timedelta(days=random.randint(0, 300))
    days = []
    while len(days) < count:
        if day.weekday() < 5:
            days.append(day)
        day += timedelta(days=3)
    return days


def apply_leave(page, day, tag):
    """Applies a one-day LOP leave for the QA employee as admin and returns its id, or None when refused."""
    reason = f"{QA_REASON} {tag}"
    page.request.post(f"{BASE_URL}/leave", headers=api_headers(page), max_redirects=0, multipart={
        "leaveId": "", "start_date": day.isoformat(), "end_date": day.isoformat(), "reason": reason,
        "policy_leave_type_id": str(LOP_LEAVE), "day_type": "full", "start_half_session": "",
        "end_half_session": "", "supporting_document": "", "user_id": str(QA_EMPLOYEE_ID), "user_ids": "",
        "shift": "morning", "is_short_notice": "0"})
    page.goto(f"{BASE_URL}/leave/manageRequests?status=pending")
    rows = page_props(page)["leaveRequests"]["data"]
    created = [r for r in rows if r["user_id"] == QA_EMPLOYEE_ID and r["reason"] == reason]
    return created[0]["id"] if created else None


def set_leave_status(page, leave_id, status, reason=QA_REASON):
    response = page.request.patch(f"{BASE_URL}/leave/{leave_id}/status", data={"status": status, "action_reason": reason},
                                  headers=api_headers(page), max_redirects=0)
    assert response.status in (200, 302, 303), f"setting leave {leave_id} to {status} failed: {response.status}"


def cancel_leave(page, leave_id, reason=QA_REASON):
    response = page.request.fetch(f"{BASE_URL}/leave/{leave_id}/cancel", method="DELETE",
                                  data={"status": "cancel", "action_reason": reason},
                                  headers=api_headers(page), max_redirects=0)
    assert response.status in (200, 302, 303), f"cancelling leave {leave_id} failed: {response.status}"


def delete_leave(page, leave_id):
    return page.request.delete(f"{BASE_URL}/leave/{leave_id}", headers=api_headers(page), max_redirects=0)


def employee_logs_today(page):
    today = date.today().isoformat()
    return props_at(page, f"{LOGS_URL}?employee_id={QA_EMPLOYEE_ID}&from_date={today}&to_date={today}")["logs"]["data"]


def logs_for_leave(page, leave_id):
    """The QA employee's audit log entries for one leave, oldest first."""
    today = date.today().isoformat()
    props = props_at(page, f"{LOGS_URL}?employee_id={QA_EMPLOYEE_ID}&from_date={today}&to_date={today}")
    return sorted([log for log in props["logs"]["data"] if log["leave_application_id"] == leave_id], key=lambda l: l["id"])


def test_lal_019_leave_lifecycle_logged():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        login(page)
        page.goto(f"{BASE_URL}/leave/dashboard")
        started = datetime.now(IST)
        plan = [("A", "approved"), ("B", "rejected"), ("C", "cancelled")]
        leave_ids = []
        problems = []
        try:
            for (key, status), day in zip(plan, free_weekdays(3)):
                leave_id = apply_leave(page, day, f"LAL-019 {key}")
                assert leave_id, f"leave {key} on {day} was refused"
                leave_ids.append(leave_id)
                if status == "cancelled":
                    cancel_leave(page, leave_id)
                else:
                    set_leave_status(page, leave_id, status)
                time.sleep(1)

                # entries are matched by leave id before deleting: deleting the leave clears that link
                logs = logs_for_leave(page, leave_id)
                shown = [r["description"] for r in table_rows(page)]
                last_id = max(log["id"] for log in employee_logs_today(page))
                response = delete_leave(page, leave_id)
                assert response.status in (200, 302, 303), f"deleting leave {key} failed: {response.status}"
                time.sleep(1)
                deleted = [log for log in employee_logs_today(page) if log["id"] > last_id]
                shown += [r["description"] for r in table_rows(page)]

                actions = [log["action"] for log in logs] + [log["action"] for log in deleted]
                if actions != ["created", status, "deleted"]:
                    problems.append(f"leave {key} ({leave_id}) logged {actions}")
                    continue
                for log in logs + deleted:
                    if log["user_id"] != QA_EMPLOYEE_ID:
                        problems.append(f"leave {key}: {log['action']} is for user {log['user_id']}")
                    if not log["actor"] or log["actor"]["name"] != "Admin User":
                        problems.append(f"leave {key}: {log['action']} action by {log['actor']}")
                    if abs((to_ist(log["created_at"]) - started).total_seconds()) > 600:
                        problems.append(f"leave {key}: {log['action']} time {log['created_at']}")
                    if log["description"] not in shown:
                        problems.append(f"leave {key}: {log['description']!r} is not in the table")
                created, middle = logs
                if created["description"] != "Submitted a loss of pay leave request for 1 day(s).":
                    problems.append(f"leave {key}: created says {created['description']!r}")
                word = "cancel" if status == "cancelled" else status
                if word not in middle["description"].lower():
                    problems.append(f"leave {key}: {status} says {middle['description']!r}")
                if status != "cancelled" and "Admin User" not in middle["description"]:
                    problems.append(f"leave {key}: {status} doesn't name the admin: {middle['description']!r}")
                if "deleted by Admin User" not in deleted[0]["description"]:
                    problems.append(f"leave {key}: deleted says {deleted[0]['description']!r}")
            assert not problems, problems
        finally:
            for leave_id in leave_ids:
                delete_leave(page, leave_id)
            browser.close()
