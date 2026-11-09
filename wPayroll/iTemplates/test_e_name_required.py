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


TEMPLATES_URL = f"{BASE_URL}/payroll/templates"
STANDARD_RULES = [(1, "percent_of_ctc", 40), (2, "percent_of_basic", 50), (3, "percent_of_basic", 40),
                  (4, "percent_of_basic", 50), (5, "balance", 0)]


def template_data(name, rules=STANDARD_RULES, description="", is_active=True):
    return {"name": name, "description": description, "is_active": is_active,
            "components": [{"salary_component_id": i, "calculation_type": t, "value": v} for i, t, v in rules]}


def test_name_required():
    """PR-074: a template without a name is refused with a "required" error."""
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=os.environ.get("HEADLESS") == "1")
        hr = open_hr(browser)

        goto(hr, TEMPLATES_URL)
        status, body = api(hr, "POST", "/payroll/templates", template_data(""))
        assert status == 422 and "name" in errors_of(body), f"{status} {body}"

        browser.close()


# ====================================================================================================
# TEST CASES
#
# Test Case: test_name_required
# Test Description:
#   PR-074: a template without a name is refused with a "required" error.
# Test Steps:
#   1. Open a browser and sign in as HR (Payroll unlocked).
#   2. Open Templates.
#   3. Send a create-template request with an empty name.
#   4. Confirm it returns 422 with a name error.
