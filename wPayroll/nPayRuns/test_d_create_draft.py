import base64
import calendar
import hashlib
import hmac
import json
import os
import struct
import time
from urllib.parse import unquote

import pytest
from playwright.sync_api import Page, sync_playwright
from utils.learning_helper import BASE_URL, goto, settle


PAY_RUNS_URL = f"{BASE_URL}/payroll/pay-runs"
# Admin Payroll pages sit behind an authenticator check. The tests reuse a verified HR session saved here; when it
# has expired they verify again with PAYROLL_HR_TOTP_SECRET (preferred) or the next unused code from
# PAYROLL_HR_RECOVERY_CODES (comma separated, each works once).
HR_STATE = os.path.expanduser(os.environ.get("PAYROLL_HR_STATE", "~/.organice/payroll_hr_state.json"))
USED_CODES = HR_STATE + ".used-codes"


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


def runs_for(hr: Page, year, month):
    runs = props_at(hr, f"{PAY_RUNS_URL}?year={year}")["payRuns"]["data"]
    return [r for r in runs if (r["period_year"], r["period_month"]) == (year, month)]


def delete_run(hr: Page, run_id):
    hr.request.delete(f"{PAY_RUNS_URL}/{run_id}", headers=api_headers(hr), max_redirects=0)


SALARIES_URL = f"{BASE_URL}/payroll/salaries"


def next_free_period(hr: Page, start=(2026, 12)):
    """The first month from `start` on without a pay run - approved runs can't be removed, so each one uses up a
    month for good."""
    year, month = start
    while runs_for(hr, year, month):
        year, month = (year + 1, 1) if month == 12 else (year, month + 1)
    return year, month


def pay_run_props(hr: Page, run_id):
    return props_at(hr, f"{PAY_RUNS_URL}/{run_id}")


def test_create_draft():
    """PR-184: creating a draft from the dialog includes every employee with a salary who isn't relieved or excluded,
    and the pay date defaults to the Settings pay day (last working day). Deleted afterwards."""
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=os.environ.get("HEADLESS") == "1")
        hr = open_hr(browser)
        year, month = next_free_period(hr)
        salaried = props_at(hr, f"{SALARIES_URL}?status=with_salary&per_page=100")["employees"]["data"]

        goto(hr, PAY_RUNS_URL)
        hr.locator("main").get_by_role("button", name="Create pay run").click()
        hr.locator("#r-month").select_option(str(month))
        hr.locator("#r-year").select_option(str(year))
        hr.get_by_role("button", name="Create draft").click()
        hr.wait_for_url("**/pay-runs/*", timeout=15000)
        run_id = int(hr.url.rstrip("/").split("/")[-1])
        try:
            run = pay_run_props(hr, run_id)
            assert run["payRun"]["status"] == "draft"
            included = {s["user"]["id"] for s in run["payslips"]}
            assert included <= {e["user"]["id"] for e in salaried}
            last = date_of_last_working_day(year, month)
            assert run["payRun"]["pay_date"] == last
        finally:
            delete_run(hr, run_id)
        assert not runs_for(hr, year, month)

        browser.close()


def date_of_last_working_day(year, month):
    day = calendar.monthrange(year, month)[1]
    while calendar.weekday(year, month, day) >= 5:
        day -= 1
    return f"{year}-{month:02d}-{day:02d}"
