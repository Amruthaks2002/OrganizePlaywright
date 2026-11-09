import base64
import hashlib
import hmac
import os
import struct
import time
from urllib.parse import unquote

import pytest
from playwright.sync_api import Page, sync_playwright
from utils.learning_helper import BASE_URL, goto, settle


# Admin Payroll pages sit behind an authenticator check. The tests reuse a verified HR session saved here; when it
# has expired they verify again with PAYROLL_HR_TOTP_SECRET (preferred) or the next unused code from
# PAYROLL_HR_RECOVERY_CODES (comma separated, each works once).
HR_STATE = os.path.expanduser(os.environ.get("PAYROLL_HR_STATE", "~/.organice/payroll_hr_state.json"))
USED_CODES = HR_STATE + ".used-codes"
QA_EMPLOYEE = "AutoUser_tNuUc"
QA_REASON = "QA payroll"


def api_headers(page: Page):
    # the meta csrf token goes stale after the SPA login, the XSRF cookie doesn't
    token = unquote(next(c["value"] for c in page.context.cookies() if c["name"] == "XSRF-TOKEN"))
    return {"X-XSRF-TOKEN": token, "X-Requested-With": "XMLHttpRequest", "Accept": "application/json"}


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


SALARIES_URL = f"{BASE_URL}/payroll/salaries"
IMPORT_HEADERS = ["Employee Number", "Employee Name", "Salary Template Name", "Gross Amount (per annum)",
                  "CTC (per annum)", "B.P Amount", "Dearness Allowance Amount", "HRA Amount", "Special Allowance Amount",
                  "Fixed Allowance", "Performance Bonus", "Is Eligible For PF", "Is Eligible For ESI", "Effective From",
                  "Revision Reason"]
QA_EMPLOYEE_NUMBER = "emp2460"


def import_csv(rows, headers=IMPORT_HEADERS):
    """CSV text for the salary import. rows: dicts keyed by header (missing columns are blank)."""
    import csv, io
    out = io.StringIO()
    writer = csv.writer(out)
    writer.writerow(headers)
    for row in rows:
        writer.writerow([row.get(h, "") for h in headers])
    return out.getvalue().encode()


def qa_import_row(**fields):
    return {"Employee Number": QA_EMPLOYEE_NUMBER, "Employee Name": QA_EMPLOYEE, "Salary Template Name": "Standard CTC",
            "CTC (per annum)": "1500000", "Is Eligible For PF": "Yes", "Is Eligible For ESI": "Yes",
            "Effective From": "2099-01-01", "Revision Reason": QA_REASON, **fields}


def import_file(content, name="salaries.csv", mime="text/csv", effective_from="2099-01-01"):
    return {"file": {"name": name, "mimeType": mime, "buffer": content}, "effective_from": effective_from}


def import_preview(hr: Page, content, **kwargs):
    """(status, body) of the import check; body has `rows` (status, errors, warnings) and a `summary`."""
    goto(hr, SALARIES_URL)
    response = hr.request.post(f"{BASE_URL}/payroll/salaries/import/preview", headers=api_headers(hr),
                               multipart=import_file(content, **kwargs))
    try:
        return response.status, response.json()
    except Exception:
        return response.status, response.text()


def test_unknown_employee():
    """PR-134: a row with an employee number nobody has (NOPE999) is reported as an error / skipped."""
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=os.environ.get("HEADLESS") == "1")
        hr = open_hr(browser)

        status, body = import_preview(hr, import_csv([qa_import_row(**{"Employee Number": "NOPE999"})]))
        row = body["rows"][0]
        assert row["status"] in ("error", "skipped") and any("NOPE999" in e for e in row["errors"]), row

        browser.close()


# ====================================================================================================
# TEST CASES
#
# Test Case: test_unknown_employee
# Test Description:
#   PR-134: a row with an employee number nobody has (NOPE999) is reported as an error / skipped.
# Test Steps:
#   1. Open a browser and sign in as HR (Payroll unlocked).
#   2. Upload a salary import CSV to the import check, with the employee number NOPE999.
#   3. Confirm the row's status is error or skipped.
#   4. Confirm its errors mention NOPE999.
