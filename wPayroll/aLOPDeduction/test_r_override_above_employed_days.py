import base64
import calendar
import hashlib
import hmac
import json
import os
import struct
import time
from contextlib import contextmanager
from urllib.parse import quote, unquote

import pytest
from playwright.sync_api import Page, expect, sync_playwright
from utils.learning_helper import BASE_URL, goto, settle


PAY_RUNS_URL = f"{BASE_URL}/payroll/pay-runs"
# Admin Payroll pages sit behind an authenticator check. The tests reuse a verified HR session saved here; when it
# has expired they verify again with PAYROLL_HR_TOTP_SECRET (preferred) or the next unused code from
# PAYROLL_HR_RECOVERY_CODES (comma separated, each works once).
HR_STATE = os.path.expanduser(os.environ.get("PAYROLL_HR_STATE", "~/.organice/payroll_hr_state.json"))
USED_CODES = HR_STATE + ".used-codes"
# Dedicated QA employee for the proration tests. Its baseline is hire = relieving = 2024-01-01, which keeps it out
# of every real pay run; a test opens the dates it needs and restores the baseline afterwards.
QA_EMPLOYEE_ID = 247
QA_EMPLOYEE = "AutoUser_tNuUc"
QA_EMPLOYEE_EMAIL = "zoBUb@testmail.com"
QA_BASELINE = ("2024-01-01", "2024-01-01")
NOT_RELIEVED = "2099-12-31"
QA_REASON = "QA payroll"


def api_headers(page: Page):
    # the meta csrf token goes stale after the SPA login, the XSRF cookie doesn't
    token = unquote(next(c["value"] for c in page.context.cookies() if c["name"] == "XSRF-TOKEN"))
    return {"X-XSRF-TOKEN": token, "X-Requested-With": "XMLHttpRequest", "Accept": "application/json"}


def page_props(page: Page):
    return json.loads(page.locator("[data-page]").first.get_attribute("data-page"))["props"]


def props_at(page: Page, url):
    goto(page, url)
    return page_props(page)


def dev_login(page: Page, role):
    page.goto(BASE_URL)
    page.get_by_test_id(f"dev-login-link-{role}").click()
    page.wait_for_url(lambda url: "/dashboard" in url or "/payroll" in url)
    settle(page)


def totp(secret):
    key = base64.b32decode(secret.upper().replace(" ", "") + "=" * (-len(secret.replace(" ", "")) % 8))
    digest = hmac.new(key, struct.pack(">Q", int(time.time()) // 30), hashlib.sha1).digest()
    offset = digest[-1] & 0x0F
    return f"{(struct.unpack('>I', digest[offset:offset + 4])[0] & 0x7FFFFFFF) % 1_000_000:06d}"


def next_recovery_code():
    codes = [c.strip() for c in os.environ.get("PAYROLL_HR_RECOVERY_CODES", "").split(",") if c.strip()]
    used = set(open(USED_CODES).read().split()) if os.path.exists(USED_CODES) else set()
    unused = [c for c in codes if c not in used]
    if not unused:
        return None
    with open(USED_CODES, "a") as f:
        f.write(unused[0] + "\n")
    return unused[0]


def verify_payroll(page: Page):
    """Gets past the Payroll authenticator check, or fails with what to set."""
    goto(page, f"{BASE_URL}/payroll")
    if "/payroll/security/verify" not in page.url:
        return
    secret = os.environ.get("PAYROLL_HR_TOTP_SECRET")
    code = totp(secret) if secret else next_recovery_code()
    if not code:
        pytest.fail("The saved Payroll HR session has expired. Set PAYROLL_HR_TOTP_SECRET, or "
                    "PAYROLL_HR_RECOVERY_CODES (unused HR recovery codes), and run again.")
    if not secret:
        page.get_by_role("button", name="Use a recovery code instead").click()
        page.get_by_placeholder("XXXXX-XXXXX").fill(code)
    else:
        page.locator("main input").first.fill(code)
    page.keyboard.press("Enter")
    page.wait_for_url(lambda url: "/payroll/security" not in url, timeout=15000)


def open_hr(browser):
    """HR page with Payroll unlocked; the verified session is saved for the next test."""
    state = HR_STATE if os.path.exists(HR_STATE) else None
    context = browser.new_context(storage_state=state, viewport={"width": 1600, "height": 900})
    page = context.new_page()
    page.goto(f"{BASE_URL}/payroll")
    if "/dashboard" not in page.url and "/payroll" not in page.url:
        dev_login(page, "hr")
    verify_payroll(page)
    os.makedirs(os.path.dirname(HR_STATE), exist_ok=True)
    context.storage_state(path=HR_STATE)
    return page


def open_admin(browser):
    page = browser.new_context(viewport={"width": 1600, "height": 900}).new_page()
    dev_login(page, "admin")
    return page


def open_browser(p):
    """(browser, hr, admin): HR runs payroll, admin edits employee dates and leaves."""
    browser = p.chromium.launch(headless=os.environ.get("HEADLESS") == "1")
    return browser, open_hr(browser), open_admin(browser)


def employee_row(admin: Page, email):
    users = props_at(admin, f"{BASE_URL}/users?search={quote(email)}")["users"]["data"]
    return next(u for u in users if u["email"].lower() == email.lower())


def save_employee_dates(admin: Page, email, hire, relieving):
    goto(admin, f"{BASE_URL}/users?search={quote(email)}")
    admin.locator("main tr").filter(has_text=email).first.get_by_role("button", name="Edit").click()
    admin.locator("#hire_date").fill(hire)
    admin.locator("#relieving_date").fill(relieving or "")
    admin.get_by_role("button", name="Save changes").click()
    expect(admin.get_by_text("Employee details updated successfully.").first).to_be_visible(timeout=10000)
    row = employee_row(admin, email)
    assert (row["hire_date"], row["relieving_date"]) == (hire, relieving), \
        f"dates not saved for {email}: {row['hire_date']} / {row['relieving_date']}"


@contextmanager
def employee_dates(admin: Page, hire, relieving=None, email=QA_EMPLOYEE_EMAIL):
    """Sets an employee's hire / relieving dates for the test and puts the old ones back afterwards.
    A relieving date can't be removed once saved (an empty field is ignored), so for the QA employee "not relieved"
    is a far-future date, and other employees are never given one they didn't already have."""
    row = employee_row(admin, email)
    before = (row["hire_date"], row["relieving_date"])
    if email == QA_EMPLOYEE_EMAIL:
        before = QA_BASELINE
        relieving = relieving or NOT_RELIEVED
    else:
        assert relieving == before[1], f"refusing to change {email}'s relieving date: it couldn't be removed again"
    save_employee_dates(admin, email, hire, relieving)
    try:
        yield
    finally:
        save_employee_dates(admin, email, *before)


def runs_for(hr: Page, year, month):
    runs = props_at(hr, f"{PAY_RUNS_URL}?year={year}")["payRuns"]["data"]
    return [r for r in runs if (r["period_year"], r["period_month"]) == (year, month)]


def create_run(hr: Page, year, month):
    existing = runs_for(hr, year, month)
    assert not existing, (f"{calendar.month_name[month]} {year} already has pay run #{existing[0]['id']} "
                          f"({existing[0]['status']}); delete it if a test left it behind")
    goto(hr, PAY_RUNS_URL)
    response = hr.request.post(PAY_RUNS_URL, data={"period_year": year, "period_month": month, "pay_date": ""},
                               headers=api_headers(hr), max_redirects=0)
    location = response.headers.get("location", "")
    assert "/pay-runs/" in location, f"creating the {month}/{year} pay run failed: {response.status} {location}"
    return int(location.rstrip("/").split("/")[-1])


def delete_run(hr: Page, run_id):
    hr.request.delete(f"{PAY_RUNS_URL}/{run_id}", headers=api_headers(hr), max_redirects=0)


@contextmanager
def pay_run(hr: Page, year, month):
    """A draft pay run for the month, deleted afterwards."""
    run_id = create_run(hr, year, month)
    try:
        yield run_id
    finally:
        delete_run(hr, run_id)


def recalculate(hr: Page, run_id):
    goto(hr, f"{PAY_RUNS_URL}/{run_id}")
    response = hr.request.post(f"{PAY_RUNS_URL}/{run_id}/recalculate", headers=api_headers(hr), max_redirects=0)
    assert response.status in (200, 302, 303), f"recalculating run {run_id} failed: {response.status}"


def run_payslips(hr: Page, run_id):
    return props_at(hr, f"{PAY_RUNS_URL}/{run_id}")["payslips"]


def payslip_row(hr: Page, run_id, user_id=QA_EMPLOYEE_ID):
    """The employee's payslip in the run, or None when the run left them out."""
    return next((p for p in run_payslips(hr, run_id) if p["user"]["id"] == user_id), None)


def add_adjustment(hr: Page, run_id, kind, employee=QA_EMPLOYEE, days=None, amount=None, reason=QA_REASON):
    """Adds a run adjustment through the dialog. kind: one_time_earning, one_time_deduction or lop_override.
    Returns True when the dialog accepted it."""
    goto(hr, f"{PAY_RUNS_URL}/{run_id}")
    before = len(page_props(hr)["adjustments"])
    hr.locator("main").get_by_role("button", name="Add adjustment").first.click()
    picker = hr.get_by_placeholder("Choose an employee")
    picker.fill(employee)
    hr.wait_for_timeout(800)
    # with a single employee in the run the picker has already chosen them and lists no options
    option = hr.get_by_role("option", name=employee)
    if option.count():
        option.first.click()
    hr.locator("label").filter(has=hr.locator(f"input[type=radio][value={kind}]")).first.click()
    if days is not None:
        hr.locator("#a-days").fill(str(days))
    if amount is not None:
        hr.locator("#a-amount").fill(str(amount))
        if hr.locator("#a-label").is_visible():
            hr.locator("#a-label").fill(reason)
    hr.locator("#a-reason").fill(reason)
    hr.get_by_role("button", name="Add adjustment").last.click()
    hr.wait_for_timeout(2000)
    return len(props_at(hr, f"{PAY_RUNS_URL}/{run_id}")["adjustments"]) > before


def test_override_above_employed_days():
    """PR-418: an employee who joined on 16 November 2025 was employed for 15 days, so an LOP override of 20 is
    rejected.
    Likely to fail: the app silently caps it (David's 5.5-day override became 4)."""
    with sync_playwright() as p:
        browser, hr, admin = open_browser(p)

        with employee_dates(admin, "2025-11-16"), pay_run(hr, 2025, 11) as run_id:
            accepted = add_adjustment(hr, run_id, "lop_override", days=20)
            recalculate(hr, run_id)
            row = payslip_row(hr, run_id)
            assert not accepted, f"an override of 20 LOP days was saved for 15 employed days (LOP now {row['lop_days']})"

        browser.close()


# ====================================================================================================
# TEST CASES
#
# Test Case: test_override_above_employed_days
# Test Description:
#   PR-418: an employee who joined on 16 November 2025 was employed for 15 days, so an LOP override of 20 is rejected.
#   Likely to fail: the app silently caps it (David's 5.5-day override became 4).
# Test Steps:
#   1. Open a browser and sign in as HR (Payroll unlocked) and as admin (Development Quick Login) in separate
#      sessions.
#   2. As admin, open Users, edit the QA employee (AutoUser_tNuUc, zoBUb@testmail.com), set the hire date to 16 Nov
#      2025 and the relieving date to 31 Dec 2099 (meaning "not relieved"), and save.
#   3. As HR, create a draft pay run for November 2025 (creating it calculates every payslip).
#   4. As HR, open Add adjustment on the pay run and try to save an LOP Days Override of 20 for the QA employee
#      (employed for only 15 days).
#   5. As HR, open the pay run and click Recalculate.
#   6. Confirm the override was refused; the failure message reports the LOP days the payslip ended up with.
#   7. Clean up (runs even if the test fails): delete the draft pay run, restore the QA employee's dates to the
#      baseline (hire = relieving = 1 Jan 2024).
