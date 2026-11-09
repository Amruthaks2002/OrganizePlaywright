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


SETTINGS_URL = f"{BASE_URL}/payroll/settings"


def payroll_settings(hr: Page):
    return props_at(hr, SETTINGS_URL)["settings"]


def test_page_shows_saved_values():
    """PR-020: the Settings form shows the saved values (legal name, address, currency, payslip prefix, pay day,
    rounding and LOP basis)."""
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=os.environ.get("HEADLESS") == "1")
        hr = open_hr(browser)
        saved = payroll_settings(hr)

        goto(hr, SETTINGS_URL)
        main = hr.locator("main")
        assert main.locator("#legal_name").input_value() == saved["legal_name"]
        assert main.locator("#address").input_value() == (saved["address"] or "")
        assert main.locator("#currency").input_value() == saved["currency"]
        assert main.locator("#payslip_prefix").input_value() == saved["payslip_prefix"]
        assert main.locator("#pay_day").input_value() == str(saved["pay_day"])
        assert main.locator("#round_to_nearest").input_value() == str(saved["round_to_nearest"])
        assert main.locator(f"input[type=radio][value={saved['lop_calculation_basis']}]").is_checked()

        browser.close()


# ====================================================================================================
# TEST CASES
#
# Test Case: test_page_shows_saved_values
# Test Description:
#   PR-020: the Settings form shows the saved values (legal name, address, currency, payslip prefix, pay day, rounding
#   and LOP basis).
# Test Steps:
#   1. Open a browser and sign in as HR (Payroll unlocked).
#   2. Read the saved Payroll settings from the page data.
#   3. Open Payroll Settings.
#   4. Confirm the legal name, address, currency, payslip prefix, pay day and rounding fields show the saved values.
#   5. Confirm the saved LOP calculation basis is the selected option.
