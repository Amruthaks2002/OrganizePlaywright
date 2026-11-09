import base64
import hashlib
import hmac
import json
import os
import struct
import time
from datetime import date

import pytest
from playwright.sync_api import Page, sync_playwright
from utils.learning_helper import BASE_URL, goto, settle


PAY_RUNS_URL = f"{BASE_URL}/payroll/pay-runs"
# Admin Payroll pages sit behind an authenticator check. The tests reuse a verified HR session saved here; when it
# has expired they verify again with PAYROLL_HR_TOTP_SECRET (preferred) or the next unused code from
# PAYROLL_HR_RECOVERY_CODES (comma separated, each works once).
HR_STATE = os.path.expanduser(os.environ.get("PAYROLL_HR_STATE", "~/.organice/payroll_hr_state.json"))
USED_CODES = HR_STATE + ".used-codes"


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


def payslip_detail(hr: Page, payslip_id):
    return props_at(hr, f"{BASE_URL}/payroll/payslips/{payslip_id}")["payslip"]


def latest_run(hr: Page, statuses=("approved", "paid")):
    """The newest pay run in one of the statuses, or None."""
    for year in range(date.today().year + 1, 2023, -1):
        for run in props_at(hr, f"{PAY_RUNS_URL}?year={year}")["payRuns"]["data"]:
            if run["status"] in statuses:
                return run
    return None


def rupee_words(amount):
    """'Rupees Ninety Six Thousand Four Hundred Only' - Indian numbering (lakh, crore)."""
    ones = ["", "One", "Two", "Three", "Four", "Five", "Six", "Seven", "Eight", "Nine", "Ten", "Eleven", "Twelve",
            "Thirteen", "Fourteen", "Fifteen", "Sixteen", "Seventeen", "Eighteen", "Nineteen"]
    tens = ["", "", "Twenty", "Thirty", "Forty", "Fifty", "Sixty", "Seventy", "Eighty", "Ninety"]

    def below_100(n):
        return ones[n] if n < 20 else (tens[n // 10] + (" " + ones[n % 10] if n % 10 else ""))

    def below_1000(n):
        return ((ones[n // 100] + " Hundred" + (" " if n % 100 else "")) if n >= 100 else "") + (below_100(n % 100) if n % 100 else "")

    n = int(amount)
    if n == 0:
        return "Rupees Zero Only"
    parts = []
    for size, name in ((10000000, "Crore"), (100000, "Lakh"), (1000, "Thousand")):
        if n >= size:
            parts.append(f"{below_1000(n // size) if size == 10000000 else below_100(n // size)} {name}")
            n %= size
    if n:
        parts.append(below_1000(n))
    return "Rupees " + " ".join(parts) + " Only"


def test_net_pay_in_words():
    """PR-172: the net pay in words matches the figure on every payslip of the latest approved run (Indian numbering,
    e.g. "Rupees Ninety Six Thousand Four Hundred Only")."""
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=os.environ.get("HEADLESS") == "1")
        hr = open_hr(browser)
        run = latest_run(hr)
        assert run, "no approved pay run"

        for slip in run_payslips(hr, run["id"]):
            detail = payslip_detail(hr, slip["id"])
            assert detail["net_pay_in_words"] == rupee_words(detail["net_pay"]), (detail["net_pay"], detail["net_pay_in_words"])

        browser.close()
