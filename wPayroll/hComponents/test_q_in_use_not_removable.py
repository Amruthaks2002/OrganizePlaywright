import base64
import hashlib
import hmac
import json
import os
import struct
import time
from contextlib import contextmanager
from urllib.parse import quote, unquote

import pytest
from playwright.sync_api import Page, expect, sync_playwright
from utils.learning_helper import BASE_URL, goto, settle


# Admin Payroll pages sit behind an authenticator check. The tests reuse a verified HR session saved here; when it
# has expired they verify again with PAYROLL_HR_TOTP_SECRET (preferred) or the next unused code from
# PAYROLL_HR_RECOVERY_CODES (comma separated, each works once).
HR_STATE = os.path.expanduser(os.environ.get("PAYROLL_HR_STATE", "~/.organice/payroll_hr_state.json"))
USED_CODES = HR_STATE + ".used-codes"
# Dedicated QA employee for the proration tests. Its baseline is hire = relieving = 2024-01-01, which keeps it out
# of every real pay run; a test opens the dates it needs and restores the baseline afterwards.
QA_EMPLOYEE_ID = 247
QA_EMPLOYEE_EMAIL = "zoBUb@testmail.com"
QA_BASELINE = ("2024-01-01", "2024-01-01")
NOT_RELIEVED = "2099-12-31"
QA_REASON = "QA payroll"


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


def open_admin(browser):
    page = browser.new_context(viewport={"width": 1600, "height": 900}).new_page()
    dev_login(page, "admin")
    return page


def open_browser(p):
    """(browser, hr, admin): HR runs payroll, admin edits employee dates and leaves."""
    browser = p.chromium.launch(headless=os.environ.get("HEADLESS") == "1")
    return browser, open_hr(browser), open_admin(browser)


def employee_row(admin: Page, email):
    users = props_at(admin, f"{BASE_URL}/users?search={quote(email)}")["users"]["data"]
    return next(u for u in users if u["email"].lower() == email.lower())


def save_employee_dates(admin: Page, email, hire, relieving):
    goto(admin, f"{BASE_URL}/users?search={quote(email)}")
    admin.locator("main tr").filter(has_text=email).first.get_by_role("button", name="Edit").click()
    admin.locator("#hire_date").fill(hire)
    admin.locator("#relieving_date").fill(relieving or "")
    admin.get_by_role("button", name="Save changes").click()
    expect(admin.get_by_text("Employee details updated successfully.").first).to_be_visible(timeout=10000)
    row = employee_row(admin, email)
    assert (row["hire_date"], row["relieving_date"]) == (hire, relieving), \
        f"dates not saved for {email}: {row['hire_date']} / {row['relieving_date']}"


@contextmanager
def employee_dates(admin: Page, hire, relieving=None, email=QA_EMPLOYEE_EMAIL):
    """Sets an employee's hire / relieving dates for the test and puts the old ones back afterwards.
    A relieving date can't be removed once saved (an empty field is ignored), so for the QA employee "not relieved"
    is a far-future date, and other employees are never given one they didn't already have."""
    row = employee_row(admin, email)
    before = (row["hire_date"], row["relieving_date"])
    if email == QA_EMPLOYEE_EMAIL:
        before = QA_BASELINE
        relieving = relieving or NOT_RELIEVED
    else:
        assert relieving == before[1], f"refusing to change {email}'s relieving date: it couldn't be removed again"
    save_employee_dates(admin, email, hire, relieving)
    try:
        yield
    finally:
        save_employee_dates(admin, email, *before)


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


COMPONENTS_URL = f"{BASE_URL}/payroll/components"
QA_PREFIX = "QA Payroll"


def components(hr: Page):
    return props_at(hr, COMPONENTS_URL)["components"]


def component_by_code(hr: Page, code):
    return next((c for c in components(hr) if c["code"] == code), None)


def component_data(**fields):
    data = {"name": "", "code": "", "type": "earning", "calculation_type": "fixed", "value": 0, "is_taxable": True,
            "is_prorated": True, "display_order": 90, "description": ""}
    data.update(fields)
    return data


def create_component(hr: Page, **fields):
    """Creates a component through the API and returns (status, body)."""
    goto(hr, COMPONENTS_URL)
    return api(hr, "POST", "/payroll/components", component_data(**fields))


def delete_component_by_code(hr: Page, code):
    found = component_by_code(hr, code)
    if found:
        api(hr, "DELETE", f"/payroll/components/{found['id']}")


@contextmanager
def qa_component(hr: Page, **fields):
    """A QA component for the test (unique name / code), deleted afterwards. Yields the component."""
    from utils.onboarding_helper import unique_tag
    tag = unique_tag().upper()
    fields = {"name": f"{QA_PREFIX} {tag}", "code": f"QA{tag}"[:10], **fields}
    status, body = create_component(hr, **fields)
    assert status in (200, 302, 303), f"creating component failed: {status} {errors_of(body)}"
    try:
        yield component_by_code(hr, fields["code"])
    finally:
        delete_component_by_code(hr, fields["code"])
        # a component that was ever on a salary (even a cancelled one) can't be deleted, so switch it off instead
        left = component_by_code(hr, fields["code"])
        if left and left["is_active"]:
            api(hr, "PATCH", f"/payroll/components/{left['id']}/toggle")


STANDARD_RULES = [(1, "percent_of_ctc", 40), (2, "percent_of_basic", 50), (3, "percent_of_basic", 40),
                  (4, "percent_of_basic", 50), (5, "balance", 0)]
SALARIES_URL = f"{BASE_URL}/payroll/salaries"
# Standard CTC with PF, ESI and PT, by component id
STATUTORY_RULES = STANDARD_RULES + [(6, "percent_of_basic", 12), (7, "percent_of_gross", 0.75), (8, "fixed", 0),
                                    (9, "percent_of_basic", 12), (10, "percent_of_gross", 3.25)]


def salary_data(annual_ctc, effective_from, rules=STATUTORY_RULES, template_id=1, reason=QA_REASON):
    return {"annual_ctc": annual_ctc, "salary_template_id": template_id, "effective_from": effective_from,
            "revision_reason": reason,
            "components": [{"salary_component_id": i, "calculation_type": t, "value": v} for i, t, v in rules]}


def salary_history(hr: Page, user_id=QA_EMPLOYEE_ID):
    return props_at(hr, f"{SALARIES_URL}/{user_id}")["history"]


@contextmanager
def scheduled_revision(hr: Page, annual_ctc, effective_from, user_id=QA_EMPLOYEE_ID, **kwargs):
    """A future-dated salary revision for the test, cancelled afterwards. Yields the revision."""
    before = {r["id"] for r in salary_history(hr, user_id)}
    status, body = api(hr, "POST", f"/payroll/salaries/{user_id}", salary_data(annual_ctc, effective_from, **kwargs))
    assert status in (200, 302, 303), f"saving the revision failed: {status} {errors_of(body)}"
    new = [r for r in salary_history(hr, user_id) if r["id"] not in before]
    try:
        yield new[0] if new else None
    finally:
        for revision in new:
            api(hr, "DELETE", f"/payroll/salaries/{user_id}/revisions/{revision['id']}")


def test_in_use_not_removable():
    """PR-056: a component used by a salary can't be switched off or deleted. Uses a QA component on a future-dated
    revision (cancelled afterwards); anything switched off is switched back on."""
    with sync_playwright() as p:
        browser, hr, admin = open_browser(p)

        with employee_dates(admin, "2024-01-01"), qa_component(hr, value=500) as component:
            with scheduled_revision(hr, 1200000, "2099-01-01", rules=STATUTORY_RULES + [(component["id"], "fixed", 500)]):
                api(hr, "PATCH", f"/payroll/components/{component['id']}/toggle")
                still_active = component_by_code(hr, component["code"])["is_active"]
                if not still_active:
                    api(hr, "PATCH", f"/payroll/components/{component['id']}/toggle")
                api(hr, "DELETE", f"/payroll/components/{component['id']}")
                still_there = component_by_code(hr, component["code"]) is not None
                assert still_active, "an in-use component was switched off"
                assert still_there, "an in-use component was deleted"

        browser.close()


# ====================================================================================================
# TEST CASES
#
# Test Case: test_in_use_not_removable
# Test Description:
#   PR-056: a component used by a salary can't be switched off or deleted. Uses a QA component on a future-dated
#   revision (cancelled afterwards); anything switched off is switched back on.
# Test Steps:
#   1. Open a browser and sign in as HR (Payroll unlocked) and as admin (Development Quick Login) in separate
#      sessions.
#   2. As admin, open Users, edit the QA employee (AutoUser_tNuUc, zoBUb@testmail.com), set the hire date to 1 Jan
#      2024 and the relieving date to 31 Dec 2099 (meaning "not relieved"), and save.
#   3. As HR, create a QA fixed component of 500.
#   4. Save a salary revision for the QA employee effective 1 Jan 2099 that includes the component.
#   5. Try to switch the component off and note whether it stayed active; if it went off, switch it back on.
#   6. Try to delete the component and note whether it is still there.
#   7. Confirm it stayed active and wasn't deleted.
#   8. Clean up (runs even if the test fails): cancel the revision, delete the component, restore the QA employee's
#      dates to the baseline (hire = relieving = 1 Jan 2024).
