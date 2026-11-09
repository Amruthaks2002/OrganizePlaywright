import base64
import csv
import hashlib
import hmac
import io
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


SALARIES_URL = f"{BASE_URL}/payroll/salaries"


def require_step_up():
    """Profile changes ask for a fresh authenticator code, which only a TOTP secret can produce."""
    if not os.environ.get("PAYROLL_HR_TOTP_SECRET"):
        pytest.skip("saving a payroll profile needs a fresh authenticator code: set PAYROLL_HR_TOTP_SECRET")


def confirm_step_up(page: Page):
    dialog = page.locator("div.fixed:visible").filter(has_text="authenticator").last
    dialog.locator("input").first.fill(totp(os.environ["PAYROLL_HR_TOTP_SECRET"]))
    dialog.get_by_role("button", name="Confirm").click()


def download_with_step_up(page: Page, url, button):
    """Downloads a file through its button. Salary exports, the bank advice and the WPS register first ask for a fresh
    authenticator code, so this needs PAYROLL_HR_TOTP_SECRET. Returns the file's bytes."""
    require_step_up()
    goto(page, url)
    with page.expect_download(timeout=30000) as download:
        page.locator("main").get_by_text(button, exact=True).first.click()
        page.wait_for_timeout(1000)
        if page.locator("div.fixed:visible").filter(has_text="authenticator").count():
            confirm_step_up(page)
    with open(download.value.path(), "rb") as f:
        return f.read()


def test_export_csv():
    """PR-130: Export CSV (after the authenticator check) downloads a CSV with a header row and one row per employee,
    and David's row has his 12 L CTC. Needs PAYROLL_HR_TOTP_SECRET."""
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=os.environ.get("HEADLESS") == "1")
        hr = open_hr(browser)
        total = props_at(hr, SALARIES_URL)["stats"]["total"]

        content = download_with_step_up(hr, SALARIES_URL, "Export CSV")
        rows = list(csv.reader(io.StringIO(content.decode("utf-8-sig"))))
        assert len(rows) - 1 == total, f"{len(rows) - 1} rows for {total} employees"
        david = next(r for r in rows if "david@iocod.com" in r or "IMP001133" in r)
        assert any(cell.replace(",", "").replace(".00", "") == "1200000" for cell in david), david

        browser.close()


# ====================================================================================================
# TEST CASES
#
# Test Case: test_export_csv
# Test Description:
#   PR-130: Export CSV (after the authenticator check) downloads a CSV with a header row and one row per employee, and
#   David's row has his 12 L CTC. Needs PAYROLL_HR_TOTP_SECRET.
# Test Steps:
#   1. The test is skipped unless PAYROLL_HR_TOTP_SECRET is set, because the download asks for an authenticator code.
#   2. Open a browser and sign in as HR (Payroll unlocked).
#   3. Read the total employee count from Employee Salaries.
#   4. Click Export CSV and enter the authenticator code when asked.
#   5. Confirm the file has a header plus one row for each employee.
#   6. Find David's row and confirm it has the CTC of 12,00,000.
