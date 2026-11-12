"""ML-029: A long value inside a mail.

Steps:
1. As admin, apply a one-day LOP leave for the QA employee (AutoUser_tNuUc, id 247) far in the future and cancel it
   with a 300-character reason.
2. Find its "Leave Application Cancelled" mail in Mail Logs and open it.

Expected: the reason is shown (the mail may shorten it with "..."), the text wraps instead of overflowing, and the
page doesn't scroll sideways.

Cleanup: the leave is deleted in a finally block. The QA employee's address is fake, so the mail goes nowhere; the
mail log entry stays.
"""
import json
import random
import time
from datetime import date, timedelta
from urllib.parse import unquote, urlencode

from playwright.sync_api import sync_playwright, expect
from utils.login_helper import login

BASE_URL = "https://organice.qc.iocod.com"
LOGS_URL = f"{BASE_URL}/mail-logs"
EMPTY_MESSAGE = "No mail has been sent yet."


def page_props(page):
    """Props of a full page load (they go stale after in-page filtering, so only use them right after goto)."""
    props = json.loads(page.locator("[data-page]").first.get_attribute("data-page"))["props"]
    if "filters" in props:
        props["filters"] = props["filters"] or {}  # the app sends [] when nothing is filtered
    return props


def props_at(page, url):
    page.goto(url)
    page.locator("main").first.wait_for(state="visible")
    time.sleep(1)
    return page_props(page)


def list_url(**filters):
    return f"{LOGS_URL}?{urlencode(filters)}"


QA_EMPLOYEE_ID = 247          # AutoUser_tNuUc, the dedicated QA employee (Morning leave policy)
QA_EMPLOYEE_NAME = "AutoUser_tNuUc"
QA_EMPLOYEE_EMAIL = "zoBUb@testmail.com"  # a fake address, so its mails go nowhere
LOP_LEAVE = 57                # "Loss of pay Leave" on the Morning policy


def api_headers(page):
    # the meta csrf token goes stale after the SPA login, the XSRF cookie doesn't
    token = unquote(next(c["value"] for c in page.context.cookies() if c["name"] == "XSRF-TOKEN"))
    return {"X-XSRF-TOKEN": token, "X-Requested-With": "XMLHttpRequest", "Accept": "application/json"}


def free_weekday():
    """A random weekday well in the future so the QA leave doesn't clash with other leaves or payroll tests."""
    day = date(2027, 6, 1) + timedelta(days=random.randint(0, 300))
    while day.weekday() >= 5:
        day += timedelta(days=1)
    return day


def apply_leave(page, day, reason):
    """Applies a one-day LOP leave for the QA employee as admin and returns its id, or None when refused."""
    page.goto(f"{BASE_URL}/leave/dashboard")
    page.request.post(f"{BASE_URL}/leave", headers=api_headers(page), max_redirects=0, multipart={
        "leaveId": "", "start_date": day.isoformat(), "end_date": day.isoformat(), "reason": reason,
        "policy_leave_type_id": str(LOP_LEAVE), "day_type": "full", "start_half_session": "",
        "end_half_session": "", "supporting_document": "", "user_id": str(QA_EMPLOYEE_ID), "user_ids": "",
        "shift": "morning", "is_short_notice": "0"})
    page.goto(f"{BASE_URL}/leave/manageRequests?status=pending")
    rows = page_props(page)["leaveRequests"]["data"]
    created = [r for r in rows if r["user_id"] == QA_EMPLOYEE_ID and r["reason"] == reason]
    return created[0]["id"] if created else None


def set_leave_status(page, leave_id, status, reason="QA mail log"):
    response = page.request.patch(f"{BASE_URL}/leave/{leave_id}/status", data={"status": status, "action_reason": reason},
                                  headers=api_headers(page), max_redirects=0)
    assert response.status in (200, 302, 303), f"setting leave {leave_id} to {status} failed: {response.status}"


def cancel_leave(page, leave_id, reason="QA mail log"):
    response = page.request.fetch(f"{BASE_URL}/leave/{leave_id}/cancel", method="DELETE",
                                  data={"status": "cancel", "action_reason": reason},
                                  headers=api_headers(page), max_redirects=0)
    assert response.status in (200, 302, 303), f"cancelling leave {leave_id} failed: {response.status}"


def delete_leave(page, leave_id):
    return page.request.delete(f"{BASE_URL}/leave/{leave_id}", headers=api_headers(page), max_redirects=0)


def mail_for_leave(page, event_type, leave_id, timeout=40):
    """The newest mail of this type sent today for the leave (matched through the detail's application_id).
    Mails are written a moment after the action, so this polls. Returns the detail's mailLog, or None."""
    today = date.today().isoformat()
    deadline = time.time() + timeout
    while True:
        mails = props_at(page, list_url(event_type=event_type, start_date=today, end_date=today))["mailLogs"]["data"]
        for mail in mails[:6]:
            detail = props_at(page, f"{LOGS_URL}/{mail['id']}")["mailLog"]
            if str(detail.get("application_id")) == str(leave_id):
                return dict(detail, id=mail["id"])
        if time.time() > deadline:
            return None
        time.sleep(4)


LONG_REASON = ("ML-029 long reason " + "lorem ipsum dolor sit amet consectetur " * 8).strip()[:300]


def test_ml_029_long_value_in_email():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        login(page)
        leave_id = None
        try:
            leave_id = apply_leave(page, free_weekday(), f"QA mail log ML-029 {random.randint(1000, 9999)}")
            assert leave_id, "the QA leave was refused"
            cancel_leave(page, leave_id, LONG_REASON)

            mail = mail_for_leave(page, "leave_cancelled", leave_id)
            assert mail, f"no Leave Cancelled mail for leave {leave_id}"
            page.goto(f"{LOGS_URL}/{mail['id']}")
            page.get_by_role("link", name="← Back to Mail Activity Logs").wait_for(state="visible")
            time.sleep(1)

            reason = page.locator("main td, main p").filter(has_text=LONG_REASON[:40]).last
            expect(reason).to_be_visible()
            sizes = reason.evaluate("e => ({sw: e.scrollWidth, cw: e.clientWidth})")
            assert sizes["sw"] <= sizes["cw"] + 1, f"the reason overflows its box: {sizes}"
            assert page.evaluate("document.documentElement.scrollWidth <= window.innerWidth"), "the page scrolls sideways"
        finally:
            if leave_id:
                delete_leave(page, leave_id)
            browser.close()
