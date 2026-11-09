import base64
import hashlib
import hmac
import json
import os
import struct
import time
from datetime import date
from urllib.parse import unquote

import pytest
from playwright.sync_api import Page, expect, sync_playwright
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


def run_payslips(hr: Page, run_id):
    return props_at(hr, f"{PAY_RUNS_URL}/{run_id}")["payslips"]


def api(page: Page, method, path, data=None):
    """(status, body) of a JSON request; validation errors come back as 422 with an `errors` dict."""
    response = page.request.fetch(f"{BASE_URL}{path}", method=method, data=data, headers=api_headers(page),
                                  max_redirects=0)
    try:
        return response.status, response.json()
    except Exception:
        return response.status, response.text()


def errors_of(body):
    return body.get("errors", {}) if isinstance(body, dict) else {}


SETTINGS_URL = f"{BASE_URL}/payroll/settings"


def payroll_settings(hr: Page):
    return props_at(hr, SETTINGS_URL)["settings"]


def put_settings(hr: Page, values):
    data = {k: v for k, v in values.items() if k not in ("id", "logo_url")}
    status, body = api(hr, "PUT", "/payroll/settings", data)
    assert status in (200, 302, 303), f"saving payroll settings failed: {status} {errors_of(body)}"


def latest_run(hr: Page, statuses=("approved", "paid")):
    """The newest pay run in one of the statuses, or None."""
    for year in range(date.today().year + 1, 2023, -1):
        for run in props_at(hr, f"{PAY_RUNS_URL}?year={year}")["payRuns"]["data"]:
            if run["status"] in statuses:
                return run
    return None


def expect_saved(page: Page):
    """Waits for a save to finish: the success toast, or the page settling when there is none."""
    try:
        expect(page.get_by_text("saved", exact=False).or_(page.get_by_text("updated", exact=False)).first).to_be_visible(timeout=8000)
    except AssertionError:
        settle(page)


def test_legal_name_on_payslip():
    """PR-022: a new legal name and address saved from the Settings page appear on payslips. Restored afterwards."""
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=os.environ.get("HEADLESS") == "1")
        hr = open_hr(browser)
        before = payroll_settings(hr)
        run = latest_run(hr)
        assert run, "no approved pay run to check a payslip on"
        payslip_id = run_payslips(hr, run["id"])[0]["id"]

        try:
            goto(hr, SETTINGS_URL)
            hr.locator("#legal_name").fill("QA Payroll Legal Name")
            hr.locator("#address").fill("QA Payroll Address, Calicut")
            hr.locator("main").get_by_role("button", name="Save settings").click()
            expect_saved(hr)
            saved = payroll_settings(hr)
            assert (saved["legal_name"], saved["address"]) == ("QA Payroll Legal Name", "QA Payroll Address, Calicut")
            goto(hr, f"{BASE_URL}/payroll/payslips/{payslip_id}")
            text = hr.locator("main").inner_text()
            assert "QA Payroll Legal Name" in text and "QA Payroll Address, Calicut" in text
        finally:
            put_settings(hr, before)

        browser.close()


# ====================================================================================================
# TEST CASES
#
# Test Case: test_legal_name_on_payslip
# Test Description:
#   PR-022: a new legal name and address saved from the Settings page appear on payslips. Restored afterwards.
# Test Steps:
#   1. Open a browser and sign in as HR (Payroll unlocked).
#   2. Note the current Payroll settings.
#   3. Find the newest approved or paid pay run (the test fails if there is none) and take its first payslip.
#   4. Open Payroll Settings, enter the legal name "QA Payroll Legal Name" and the address "QA Payroll Address,
#      Calicut", and click Save settings.
#   5. Wait for the save, then confirm both values are saved.
#   6. Open the payslip page and confirm it shows the new legal name and address.
#   7. Clean up (runs even if the test fails): save the original Payroll settings back.
