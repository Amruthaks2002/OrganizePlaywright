import base64
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
# Dedicated QA employee for the proration tests. Its baseline is hire = relieving = 2024-01-01, which keeps it out
# of every real pay run; a test opens the dates it needs and restores the baseline afterwards.
QA_EMPLOYEE_ID = 247
DAVID_EMAIL = "david@iocod.com"
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


def runs_for(hr: Page, year, month):
    runs = props_at(hr, f"{PAY_RUNS_URL}?year={year}")["payRuns"]["data"]
    return [r for r in runs if (r["period_year"], r["period_month"]) == (year, month)]


def delete_run(hr: Page, run_id):
    hr.request.delete(f"{PAY_RUNS_URL}/{run_id}", headers=api_headers(hr), max_redirects=0)


def open_david(browser):
    page = browser.new_context(viewport={"width": 1600, "height": 900}).new_page()
    page.goto(BASE_URL)
    page.fill("#email", DAVID_EMAIL)
    page.fill("#password", "password")
    page.get_by_test_id("sign-in-button").click()
    page.wait_for_url("**/dashboard**")
    settle(page)
    return page


def api(page: Page, method, path, data=None):
    """(status, body) of a JSON request; validation errors come back as 422 with an `errors` dict."""
    response = page.request.fetch(f"{BASE_URL}{path}", method=method, data=data, headers=api_headers(page),
                                  max_redirects=0)
    try:
        return response.status, response.json()
    except Exception:
        return response.status, response.text()


SETTINGS_URL = f"{BASE_URL}/payroll/settings"


def payroll_settings(hr: Page):
    return props_at(hr, SETTINGS_URL)["settings"]


COMPONENTS_URL = f"{BASE_URL}/payroll/components"


def components(hr: Page):
    return props_at(hr, COMPONENTS_URL)["components"]


def component_by_code(hr: Page, code):
    return next((c for c in components(hr) if c["code"] == code), None)


def component_data(**fields):
    data = {"name": "", "code": "", "type": "earning", "calculation_type": "fixed", "value": 0, "is_taxable": True,
            "is_prorated": True, "display_order": 90, "description": ""}
    data.update(fields)
    return data


def delete_component_by_code(hr: Page, code):
    found = component_by_code(hr, code)
    if found:
        api(hr, "DELETE", f"/payroll/components/{found['id']}")


STANDARD_RULES = [(1, "percent_of_ctc", 40), (2, "percent_of_basic", 50), (3, "percent_of_basic", 40),
                  (4, "percent_of_basic", 50), (5, "balance", 0)]
SALARIES_URL = f"{BASE_URL}/payroll/salaries"
# Standard CTC with PF, ESI and PT, by component id
STATUTORY_RULES = STANDARD_RULES + [(6, "percent_of_basic", 12), (7, "percent_of_gross", 0.75), (8, "fixed", 0),
                                    (9, "percent_of_basic", 12), (10, "percent_of_gross", 3.25)]


def salary_data(annual_ctc, effective_from, rules=STATUTORY_RULES, template_id=1, reason=QA_REASON):
    return {"annual_ctc": annual_ctc, "salary_template_id": template_id, "effective_from": effective_from,
            "revision_reason": reason,
            "components": [{"salary_component_id": i, "calculation_type": t, "value": v} for i, t, v in rules]}


def salary_history(hr: Page, user_id=QA_EMPLOYEE_ID):
    return props_at(hr, f"{SALARIES_URL}/{user_id}")["history"]


def test_admin_actions_forbidden():
    """PR-009: an employee's direct requests to admin actions - create a pay run, create a component, save settings,
    assign a salary - get 403 and change nothing. (Anything that does get created is removed again.)"""
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=os.environ.get("HEADLESS") == "1")
        hr, david = open_hr(browser), open_david(browser)
        settings = payroll_settings(hr)
        revisions = {r["id"] for r in salary_history(hr)}
        goto(david, f"{BASE_URL}/payroll/my/salary")

        try:
            statuses = {
                "create pay run": api(david, "POST", "/payroll/pay-runs",
                                      {"period_year": 2099, "period_month": 1, "pay_date": ""})[0],
                "create component": api(david, "POST", "/payroll/components",
                                        component_data(name="QA forbidden", code="QAFORBID"))[0],
                "save settings": api(david, "PUT", "/payroll/settings", settings)[0],
                "assign salary": api(david, "POST", f"/payroll/salaries/{QA_EMPLOYEE_ID}",
                                     salary_data(1200000, "2099-01-01"))[0],
            }
            assert all(s == 403 for s in statuses.values()), f"not refused: {statuses}"
        finally:
            for run in runs_for(hr, 2099, 1):
                delete_run(hr, run["id"])
            delete_component_by_code(hr, "QAFORBID")
            for revision in salary_history(hr):
                if revision["id"] not in revisions:
                    api(hr, "DELETE", f"/payroll/salaries/{QA_EMPLOYEE_ID}/revisions/{revision['id']}")

        browser.close()


# ====================================================================================================
# TEST CASES
#
# Test Case: test_admin_actions_forbidden
# Test Description:
#   PR-009: an employee's direct requests to admin actions - create a pay run, create a component, save settings,
#   assign a salary - get 403 and change nothing. (Anything that does get created is removed again.)
# Test Steps:
#   1. Open a browser and sign in as HR and as David in separate sessions.
#   2. As HR, note the current Payroll settings and the QA employee's salary revisions.
#   3. As David, open My Salary so the session has a valid token.
#   4. As David, send direct requests to create a pay run for January 2099, create a component with code QAFORBID,
#      save the settings, and assign the QA employee a salary.
#   5. Confirm all four requests return 403.
#   6. Clean up (runs even if the test fails): as HR, delete any January 2099 pay run, delete any QAFORBID component,
#      delete any salary revision that wasn't there before.
