import base64
import hashlib
import hmac
import json
import os
import struct
import time
from urllib.parse import unquote

import pytest
from playwright.sync_api import Page, expect, sync_playwright
from utils.learning_helper import BASE_URL, goto, settle
from utils.onboarding_helper import unique_tag


# Admin Payroll pages sit behind an authenticator check. The tests reuse a verified HR session saved here; when it
# has expired they verify again with PAYROLL_HR_TOTP_SECRET (preferred) or the next unused code from
# PAYROLL_HR_RECOVERY_CODES (comma separated, each works once).
HR_STATE = os.path.expanduser(os.environ.get("PAYROLL_HR_STATE", "~/.organice/payroll_hr_state.json"))
USED_CODES = HR_STATE + ".used-codes"
# Dedicated QA employee for the proration tests. Its baseline is hire = relieving = 2024-01-01, which keeps it out
# of every real pay run; a test opens the dates it needs and restores the baseline afterwards.
QA_EMPLOYEE_ID = 247


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


def api(page: Page, method, path, data=None):
    """(status, body) of a JSON request; validation errors come back as 422 with an `errors` dict."""
    response = page.request.fetch(f"{BASE_URL}{path}", method=method, data=data, headers=api_headers(page),
                                  max_redirects=0)
    try:
        return response.status, response.json()
    except Exception:
        return response.status, response.text()


COMPONENTS_URL = f"{BASE_URL}/payroll/components"
TEMPLATES_URL = f"{BASE_URL}/payroll/templates"
QA_PREFIX = "QA Payroll"


def components(hr: Page):
    return props_at(hr, COMPONENTS_URL)["components"]


def component_by_code(hr: Page, code):
    return next((c for c in components(hr) if c["code"] == code), None)


def delete_component_by_code(hr: Page, code):
    found = component_by_code(hr, code)
    if found:
        api(hr, "DELETE", f"/payroll/components/{found['id']}")


SALARIES_URL = f"{BASE_URL}/payroll/salaries"


def test_create_earning():
    """PR-045: a custom fixed earning of 1,000 created from the New component dialog is listed and offered on the
    template and assign-salary forms. Deleted afterwards."""
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=os.environ.get("HEADLESS") == "1")
        hr = open_hr(browser)
        tag = unique_tag().upper()
        name, code = f"{QA_PREFIX} {tag}", f"QA{tag}"[:10]

        try:
            goto(hr, COMPONENTS_URL)
            hr.locator("main").get_by_role("button", name="New component").click()
            hr.locator("#c-name").fill(name)
            hr.locator("#c-code").fill(code)
            hr.locator("#c-value").fill("1000")
            hr.get_by_role("button", name="Create component").click()
            expect(hr.locator("main tbody tr").filter(has_text=code)).to_have_count(1, timeout=10000)
            created = next(c for c in components(hr) if c["code"] == code)
            assert (created["type"], created["calculation_type"], created["value"]) == ("earning", "fixed", 1000)
            assert code in [c["code"] for c in props_at(hr, f"{TEMPLATES_URL}/create")["components"]]
            assert code in [c["code"] for c in props_at(hr, f"{SALARIES_URL}/{QA_EMPLOYEE_ID}/assign")["components"]]
        finally:
            delete_component_by_code(hr, code)

        browser.close()


# ====================================================================================================
# TEST CASES
#
# Test Case: test_create_earning
# Test Description:
#   PR-045: a custom fixed earning of 1,000 created from the New component dialog is listed and offered on the
#   template and assign-salary forms. Deleted afterwards.
# Test Steps:
#   1. Open a browser and sign in as HR (Payroll unlocked).
#   2. Open Salary Components and click New component.
#   3. Enter a unique QA name and code, a value of 1000 and click Create component.
#   4. Confirm exactly one row with that code appears.
#   5. Confirm it was saved as a fixed earning of 1,000.
#   6. Confirm it is offered on the New template form.
#   7. Confirm it is offered on the QA employee's assign-salary form.
#   8. Clean up (runs even if the test fails): delete the component.
