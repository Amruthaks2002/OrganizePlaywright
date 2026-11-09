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
# Dedicated QA employee for the proration tests. Its baseline is hire = relieving = 2024-01-01, which keeps it out
# of every real pay run; a test opens the dates it needs and restores the baseline afterwards.
QA_EMPLOYEE_ID = 247


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


SALARIES_URL = f"{BASE_URL}/payroll/salaries"


def require_step_up():
    """Profile changes ask for a fresh authenticator code, which only a TOTP secret can produce."""
    if not os.environ.get("PAYROLL_HR_TOTP_SECRET"):
        pytest.skip("saving a payroll profile needs a fresh authenticator code: set PAYROLL_HR_TOTP_SECRET")


def confirm_step_up(page: Page):
    dialog = page.locator("div.fixed:visible").filter(has_text="authenticator").last
    dialog.locator("input").first.fill(totp(os.environ["PAYROLL_HR_TOTP_SECRET"]))
    dialog.get_by_role("button", name="Confirm").click()


FIELDS = {"PAN NUMBER": "B5014Q", "IFSC CODE": "SBI12", "UNIVERSAL ACCOUNT NO. (UAN)": "12345"}


def test_profile_validation():
    """PR-114: an invalid PAN (B5014Q), IFSC (SBI12) or UAN (5 digits) is refused and not saved. Needs
    PAYROLL_HR_TOTP_SECRET. Likely to fail: B5014Q was accepted during exploration."""
    require_step_up()
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=os.environ.get("HEADLESS") == "1")
        hr = open_hr(browser)
        before = props_at(hr, f"{SALARIES_URL}/{QA_EMPLOYEE_ID}")["profile"]

        saved = []
        for label, value in FIELDS.items():
            goto(hr, f"{SALARIES_URL}/{QA_EMPLOYEE_ID}")
            hr.locator("main").get_by_text(label, exact=True).locator("xpath=following::input[1]").fill(value)
            hr.locator("main").get_by_role("button", name="Save profile changes").click()
            confirm_step_up(hr)
            hr.wait_for_timeout(2000)
            if value in props_at(hr, f"{SALARIES_URL}/{QA_EMPLOYEE_ID}")["profile"].values():
                saved.append(f"{label}={value}")
        assert not saved, f"invalid values saved: {saved} (profile was {before})"

        browser.close()


# ====================================================================================================
# TEST CASES
#
# Test Case: test_profile_validation
# Test Description:
#   PR-114: an invalid PAN (B5014Q), IFSC (SBI12) or UAN (5 digits) is refused and not saved. Needs
#   PAYROLL_HR_TOTP_SECRET. Likely to fail: B5014Q was accepted during exploration.
# Test Steps:
#   1. The test is skipped unless PAYROLL_HR_TOTP_SECRET is set, because the save asks for an authenticator code.
#   2. Open a browser and sign in as HR (Payroll unlocked).
#   3. Note the QA employee's payroll profile.
#   4. Open the salary page, enter the PAN B5014Q, click Save profile changes and enter the authenticator code.
#   5. Read the profile and note whether the value was saved.
#   6. Repeat with the IFSC code SBI12.
#   7. Repeat with the 5-digit UAN 12345.
#   8. Confirm none was saved; the failure message lists any that were.
