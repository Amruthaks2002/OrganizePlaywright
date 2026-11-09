import base64
import hashlib
import hmac
import json
import os
import struct
import time

import pytest
from playwright.sync_api import Page, sync_playwright
from utils.learning_helper import BASE_URL, goto, settle


PAY_RUNS_URL = f"{BASE_URL}/payroll/pay-runs"
# Admin Payroll pages sit behind an authenticator check. The tests reuse a verified HR session saved here; when it
# has expired they verify again with PAYROLL_HR_TOTP_SECRET (preferred) or the next unused code from
# PAYROLL_HR_RECOVERY_CODES (comma separated, each works once).
HR_STATE = os.path.expanduser(os.environ.get("PAYROLL_HR_STATE", "~/.organice/payroll_hr_state.json"))
USED_CODES = HR_STATE + ".used-codes"
DAVID_ID = 298
DAVID_EMAIL = "david@iocod.com"


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


def run_payslips(hr: Page, run_id):
    return props_at(hr, f"{PAY_RUNS_URL}/{run_id}")["payslips"]


def open_david(browser):
    page = browser.new_context(viewport={"width": 1600, "height": 900}).new_page()
    page.goto(BASE_URL)
    page.fill("#email", DAVID_EMAIL)
    page.fill("#password", "password")
    page.get_by_test_id("sign-in-button").click()
    page.wait_for_url("**/dashboard**")
    settle(page)
    return page


def status_of(page: Page, path):
    return page.request.get(f"{BASE_URL}{path}", max_redirects=0).status


def a_payslip_of_someone_else(hr: Page, user_id):
    """(payslip id, owner) of a finalized payslip that doesn't belong to user_id, from the newest approved run."""
    for year in (2027, 2026, 2025):
        for run in props_at(hr, f"{PAY_RUNS_URL}?year={year}")["payRuns"]["data"]:
            if run["status"] in ("approved", "paid"):
                for slip in run_payslips(hr, run["id"]):
                    if slip["user"]["id"] != user_id:
                        return slip["id"], slip["user"]["name"]
    return None, None


def test_others_payslip_forbidden():
    """PR-007 / PR-008: an employee (David) gets 403 opening, or downloading the PDF of, someone else's payslip."""
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=os.environ.get("HEADLESS") == "1")
        hr, david = open_hr(browser), open_david(browser)

        payslip_id, owner = a_payslip_of_someone_else(hr, DAVID_ID)
        assert payslip_id, "no finalized payslip of another employee to try"
        assert status_of(david, f"/payroll/payslips/{payslip_id}") == 403, f"David can open {owner}'s payslip"
        assert status_of(david, f"/payroll/payslips/{payslip_id}/download") == 403, f"David can download {owner}'s payslip"

        browser.close()


# ====================================================================================================
# TEST CASES
#
# Test Case: test_others_payslip_forbidden
# Test Description:
#   PR-007 / PR-008: an employee (David) gets 403 opening, or downloading the PDF of, someone else's payslip.
# Test Steps:
#   1. Open a browser and sign in as HR and as David in separate sessions.
#   2. As HR, find a finalized payslip belonging to another employee in the newest approved or paid run, and confirm
#      one exists.
#   3. As David, request that payslip's page and confirm it returns 403.
#   4. As David, request that payslip's PDF download and confirm it returns 403.
