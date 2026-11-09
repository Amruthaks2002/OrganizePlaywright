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


COMPONENTS_URL = f"{BASE_URL}/payroll/components"


def components(hr: Page):
    return props_at(hr, COMPONENTS_URL)["components"]


def test_display_order():
    """PR-062: within each classification the components list follows display order."""
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=os.environ.get("HEADLESS") == "1")
        hr = open_hr(browser)
        rows = components(hr)

        goto(hr, COMPONENTS_URL)
        codes = {c["code"] for c in rows}
        # grouped by classification (earnings, deductions, reimbursements, employer contributions), then display order
        groups = ["earning", "deduction", "reimbursement", "employer_contribution"]
        expected = [c["code"] for c in sorted(rows, key=lambda c: (groups.index(c["type"]), c["display_order"]))]
        # each row shows its code on a line of its own
        shown = [code for text in hr.locator("main tbody tr").all_inner_texts()
                 for code in [next((line.strip() for line in text.splitlines() if line.strip() in codes), None)] if code]
        assert shown == expected

        browser.close()


# ====================================================================================================
# TEST CASES
#
# Test Case: test_display_order
# Test Description:
#   PR-062: within each classification the components list follows display order.
# Test Steps:
#   1. Open a browser and sign in as HR (Payroll unlocked).
#   2. Read all the components from the page data and sort them by classification (earnings, deductions,
#      reimbursements, employer contributions), then display order.
#   3. Open Salary Components and read the codes from the table, top to bottom.
#   4. Confirm they are in the same order.
