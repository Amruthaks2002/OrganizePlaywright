"""PR-201, 203, 204, 205, 207, 209, 102, 225, 300, 305: one pay run taken all the way through.

Approving a run can't be undone and each month allows one run, so every test here shares a single run in the next
free month from December 2026 (agreed with the user: approved / paid runs stay as permanent QC data). The tests run in
file order and each checks one step. The QA employee is opened up for the month and put back afterwards; the QA
component and template are deleted.
"""
import base64
import calendar
import hashlib
import hmac
import json
import os
import re
import struct
import time
from contextlib import contextmanager
from urllib.parse import quote, unquote

import pytest
from playwright.sync_api import Page, expect, sync_playwright
from utils.learning_helper import BASE_URL, goto, settle


PAY_RUNS_URL = f"{BASE_URL}/payroll/pay-runs"
# Admin Payroll pages sit behind an authenticator check. The tests reuse a verified HR session saved here; when it
# has expired they verify again with PAYROLL_HR_TOTP_SECRET (preferred) or the next unused code from
# PAYROLL_HR_RECOVERY_CODES (comma separated, each works once).
HR_STATE = os.path.expanduser(os.environ.get("PAYROLL_HR_STATE", "~/.organice/payroll_hr_state.json"))
USED_CODES = HR_STATE + ".used-codes"
# Dedicated QA employee for the proration tests. Its baseline is hire = relieving = 2024-01-01, which keeps it out
# of every real pay run; a test opens the dates it needs and restores the baseline afterwards.
QA_EMPLOYEE_ID = 247
QA_EMPLOYEE = "AutoUser_tNuUc"
QA_EMPLOYEE_EMAIL = "zoBUb@testmail.com"
QA_BASELINE = ("2024-01-01", "2024-01-01")
NOT_RELIEVED = "2099-12-31"
DAVID_ID = 298
DAVID_EMAIL = "david@iocod.com"
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


def runs_for(hr: Page, year, month):
    runs = props_at(hr, f"{PAY_RUNS_URL}?year={year}")["payRuns"]["data"]
    return [r for r in runs if (r["period_year"], r["period_month"]) == (year, month)]


def create_run(hr: Page, year, month):
    existing = runs_for(hr, year, month)
    assert not existing, (f"{calendar.month_name[month]} {year} already has pay run #{existing[0]['id']} "
                          f"({existing[0]['status']}); delete it if a test left it behind")
    goto(hr, PAY_RUNS_URL)
    response = hr.request.post(PAY_RUNS_URL, data={"period_year": year, "period_month": month, "pay_date": ""},
                               headers=api_headers(hr), max_redirects=0)
    location = response.headers.get("location", "")
    assert "/pay-runs/" in location, f"creating the {month}/{year} pay run failed: {response.status} {location}"
    return int(location.rstrip("/").split("/")[-1])


def recalculate(hr: Page, run_id):
    goto(hr, f"{PAY_RUNS_URL}/{run_id}")
    response = hr.request.post(f"{PAY_RUNS_URL}/{run_id}/recalculate", headers=api_headers(hr), max_redirects=0)
    assert response.status in (200, 302, 303), f"recalculating run {run_id} failed: {response.status}"


def run_payslips(hr: Page, run_id):
    return props_at(hr, f"{PAY_RUNS_URL}/{run_id}")["payslips"]


def payslip_row(hr: Page, run_id, user_id=QA_EMPLOYEE_ID):
    """The employee's payslip in the run, or None when the run left them out."""
    return next((p for p in run_payslips(hr, run_id) if p["user"]["id"] == user_id), None)


def add_adjustment(hr: Page, run_id, kind, employee=QA_EMPLOYEE, days=None, amount=None, reason=QA_REASON):
    """Adds a run adjustment through the dialog. kind: one_time_earning, one_time_deduction or lop_override.
    Returns True when the dialog accepted it."""
    goto(hr, f"{PAY_RUNS_URL}/{run_id}")
    before = len(page_props(hr)["adjustments"])
    hr.locator("main").get_by_role("button", name="Add adjustment").first.click()
    picker = hr.get_by_placeholder("Choose an employee")
    picker.fill(employee)
    hr.wait_for_timeout(800)
    # with a single employee in the run the picker has already chosen them and lists no options
    option = hr.get_by_role("option", name=employee)
    if option.count():
        option.first.click()
    hr.locator("label").filter(has=hr.locator(f"input[type=radio][value={kind}]")).first.click()
    if days is not None:
        hr.locator("#a-days").fill(str(days))
    if amount is not None:
        hr.locator("#a-amount").fill(str(amount))
        if hr.locator("#a-label").is_visible():
            hr.locator("#a-label").fill(reason)
    hr.locator("#a-reason").fill(reason)
    hr.get_by_role("button", name="Add adjustment").last.click()
    hr.wait_for_timeout(2000)
    return len(props_at(hr, f"{PAY_RUNS_URL}/{run_id}")["adjustments"]) > before


def open_david(browser):
    page = browser.new_context(viewport={"width": 1600, "height": 900}).new_page()
    page.goto(BASE_URL)
    page.fill("#email", DAVID_EMAIL)
    page.fill("#password", "password")
    page.get_by_test_id("sign-in-button").click()
    page.wait_for_url("**/dashboard**")
    settle(page)
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


COMPONENTS_URL = f"{BASE_URL}/payroll/components"
TEMPLATES_URL = f"{BASE_URL}/payroll/templates"
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


def templates(hr: Page):
    return props_at(hr, TEMPLATES_URL)["templates"]


def template_by_name(hr: Page, name):
    return next((t for t in templates(hr) if t["name"] == name), None)


STANDARD_RULES = [(1, "percent_of_ctc", 40), (2, "percent_of_basic", 50), (3, "percent_of_basic", 40),
                  (4, "percent_of_basic", 50), (5, "balance", 0)]


def template_data(name, rules=STANDARD_RULES, description="", is_active=True):
    return {"name": name, "description": description, "is_active": is_active,
            "components": [{"salary_component_id": i, "calculation_type": t, "value": v} for i, t, v in rules]}


@contextmanager
def qa_template(hr: Page, rules=STANDARD_RULES, **fields):
    from utils.onboarding_helper import unique_tag
    name = f"{QA_PREFIX} template {unique_tag()}"
    goto(hr, TEMPLATES_URL)
    status, body = api(hr, "POST", "/payroll/templates", {**template_data(name, rules), **fields})
    assert status in (200, 302, 303), f"creating template failed: {status} {errors_of(body)}"
    try:
        yield template_by_name(hr, name)
    finally:
        found = template_by_name(hr, name)
        if found:
            api(hr, "DELETE", f"/payroll/templates/{found['id']}")


SALARIES_URL = f"{BASE_URL}/payroll/salaries"
# Standard CTC with PF, ESI and PT, by component id
STATUTORY_RULES = STANDARD_RULES + [(6, "percent_of_basic", 12), (7, "percent_of_gross", 0.75), (8, "fixed", 0),
                                    (9, "percent_of_basic", 12), (10, "percent_of_gross", 3.25)]


def salary_data(annual_ctc, effective_from, rules=STATUTORY_RULES, template_id=1, reason=QA_REASON):
    return {"annual_ctc": annual_ctc, "salary_template_id": template_id, "effective_from": effective_from,
            "revision_reason": reason,
            "components": [{"salary_component_id": i, "calculation_type": t, "value": v} for i, t, v in rules]}


def next_free_period(hr: Page, start=(2026, 12)):
    """The first month from `start` on without a pay run - approved runs can't be removed, so each one uses up a
    month for good."""
    year, month = start
    while runs_for(hr, year, month):
        year, month = (year + 1, 1) if month == 12 else (year, month + 1)
    return year, month


def run_action(hr: Page, run_id, action, data=None):
    goto(hr, f"{PAY_RUNS_URL}/{run_id}")
    return api(hr, "POST", f"/payroll/pay-runs/{run_id}/{action}", data or {})


def pay_run_props(hr: Page, run_id):
    return props_at(hr, f"{PAY_RUNS_URL}/{run_id}")


def modal_button(page: Page, name):
    """Clicks a button in the topmost dialog."""
    page.locator("div.fixed:visible").get_by_role("button", name=name, exact=False).last.click()
    page.wait_for_timeout(1000)


@pytest.fixture(scope="module")
def cycle():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=os.environ.get("HEADLESS") == "1")
        hr, admin, david = open_hr(browser), open_admin(browser), open_david(browser)
        year, month = next_free_period(hr)
        with employee_dates(admin, "2024-01-01"), qa_component(hr, value=1500) as component, qa_template(hr) as template:
            run_id = create_run(hr, year, month)
            yield {"hr": hr, "david": david, "run_id": run_id, "year": year, "month": month,
                   "component": component, "template": template}
        browser.close()


def test_a_component_and_template_offered(cycle):
    """PR-300 (start): a new component and template are offered on the assign-salary form."""
    hr = cycle["hr"]
    form = props_at(hr, f"{SALARIES_URL}/{QA_EMPLOYEE_ID}/assign")
    assert cycle["component"]["code"] in [c["code"] for c in form["components"]]
    assert cycle["template"]["name"] in [t["name"] for t in form["templates"]]


def test_b_submit_revert_edit_resubmit(cycle):
    """PR-305: add a one-time earning, submit, revert to draft, add a one-time deduction, resubmit - the run in
    review carries both changes (+2,000 earning, -500 deduction on the QA employee)."""
    hr, run_id = cycle["hr"], cycle["run_id"]
    before = payslip_row(hr, run_id)
    assert add_adjustment(hr, run_id, "one_time_earning", amount=2000)
    recalculate(hr, run_id)
    run_action(hr, run_id, "submit")
    assert pay_run_props(hr, run_id)["payRun"]["status"] == "in_review"
    run_action(hr, run_id, "revert")
    assert add_adjustment(hr, run_id, "one_time_deduction", amount=500)
    recalculate(hr, run_id)
    run_action(hr, run_id, "submit")
    after = payslip_row(hr, run_id)
    assert pay_run_props(hr, run_id)["payRun"]["status"] == "in_review"
    assert after["net_pay"] == before["net_pay"] + 1500


def test_c_approve_finalizes_payslips(cycle):
    """PR-201: approving from the page ("Approve & lock pay run") finalizes and numbers every payslip
    (PS-YYYYMM-NNNN) and locks the figures."""
    hr, run_id = cycle["hr"], cycle["run_id"]
    goto(hr, f"{PAY_RUNS_URL}/{run_id}")
    hr.locator("main").get_by_role("button", name="Approve & lock pay run").click()
    modal_button(hr, "Approve & lock")
    props = pay_run_props(hr, run_id)
    assert props["payRun"]["status"] == "approved"
    prefix = f"PS-{cycle['year']}{cycle['month']:02d}-"
    for slip in props["payslips"]:
        assert slip["status"] == "finalized", slip
        assert re.fullmatch(rf"{prefix}\d{{4}}", slip["payslip_number"]), slip["payslip_number"]
    assert not props["payRun"]["can"]["edit"]


def test_d_approved_not_cancellable(cycle):
    """PR-207: an approved run can't be cancelled or deleted."""
    hr, run_id = cycle["hr"], cycle["run_id"]
    run_action(hr, run_id, "cancel")
    api(hr, "DELETE", f"/payroll/pay-runs/{run_id}")
    assert pay_run_props(hr, run_id)["payRun"]["status"] == "approved"


def test_e_revision_in_approved_month_refused(cycle):
    """PR-102: a salary revision dated inside the approved month is refused. (If the app accepts it, the QA employee
    is left with an extra revision that can't be removed.)"""
    hr = cycle["hr"]
    goto(hr, f"{SALARIES_URL}/{QA_EMPLOYEE_ID}")
    status, _ = api(hr, "POST", f"/payroll/salaries/{QA_EMPLOYEE_ID}",
                    salary_data(1300000, f"{cycle['year']}-{cycle['month']:02d}-01"))
    assert status == 422, f"a revision inside an approved month was accepted ({status})"


def test_f_record_payment(cycle):
    """PR-204: recording a cheque payment for one employee marks only that payslip paid; the run stays approved."""
    hr, run_id = cycle["hr"], cycle["run_id"]
    slip = payslip_row(hr, run_id)
    goto(hr, f"{PAY_RUNS_URL}/{run_id}")
    status, body = api(hr, "POST", f"/payroll/pay-runs/{run_id}/payments",
                       {"payslip_ids": [slip["id"]], "payment_mode": "cheque", "paid_on": f"{cycle['year']}-{cycle['month']:02d}-28",
                        "payment_reference": "QA-CHQ-1"})
    assert status in (200, 302, 303), f"{status} {body}"
    props = pay_run_props(hr, run_id)
    paid = next(s for s in props["payslips"] if s["id"] == slip["id"])
    assert (paid["payment_mode"], paid["payment_reference"]) == ("cheque", "QA-CHQ-1") and paid["paid_on"]
    assert props["payRun"]["status"] == "approved"


def test_g_mark_paid_before_pay_date_refused(cycle):
    """PR-205: the run can't be marked paid with a date before its pay date (here: today, weeks before it).
    Likely to fail: the November 2026 run was marked paid 27 days early."""
    hr, run_id = cycle["hr"], cycle["run_id"]
    goto(hr, f"{PAY_RUNS_URL}/{run_id}")
    hr.locator("main").get_by_role("button", name="Mark as paid").click()
    modal_button(hr, "Mark as paid")
    assert pay_run_props(hr, run_id)["payRun"]["status"] == "approved", "marked paid before the pay date"


def test_h_mark_paid(cycle):
    """PR-203: marking the run paid on its pay date records every unpaid payslip as paid and the run as Paid."""
    hr, run_id = cycle["hr"], cycle["run_id"]
    props = pay_run_props(hr, run_id)
    if props["payRun"]["status"] != "paid":
        goto(hr, f"{PAY_RUNS_URL}/{run_id}")
        hr.locator("main").get_by_role("button", name="Mark as paid").click()
        hr.locator("#p-date").fill(props["payRun"]["pay_date"])
        modal_button(hr, "Mark as paid")
    props = pay_run_props(hr, run_id)
    assert props["payRun"]["status"] == "paid"
    assert all(s["paid_on"] for s in props["payslips"] if s["status"] != "excluded")


def test_i_paid_run_actions(cycle):
    """PR-209: a paid run only offers emailing payslips, the bank advice and the WPS register."""
    can = pay_run_props(cycle["hr"], cycle["run_id"])["payRun"]["can"]
    assert [k for k, v in can.items() if v] == ["email"]


def test_j_email_davids_payslip(cycle):
    """PR-225: emailing David's payslip from its page records when it was emailed. (Only David is emailed.)"""
    hr, run_id = cycle["hr"], cycle["run_id"]
    slip = payslip_row(hr, run_id, DAVID_ID)
    goto(hr, f"{BASE_URL}/payroll/payslips/{slip['id']}")
    hr.locator("main").get_by_role("button", name="Email payslip").click()
    if hr.locator("div.fixed:visible").count():
        modal_button(hr, "Send")
    expect(hr.locator("main")).to_contain_text("mail", timeout=10000)
    assert payslip_row(hr, run_id, DAVID_ID)["emailed_at"]


def test_k_employee_sees_payslip(cycle):
    """PR-300 (end): David sees the new payslip in My Payslips and can download it as a PDF."""
    david, hr, run_id = cycle["david"], cycle["hr"], cycle["run_id"]
    slip = payslip_row(hr, run_id, DAVID_ID)
    mine = props_at(david, f"{BASE_URL}/payroll/my/payslips?year={cycle['year']}")["payslips"]
    assert slip["id"] in [s["id"] for s in mine]
    response = david.request.get(f"{BASE_URL}/payroll/payslips/{slip['id']}/download")
    assert response.status == 200 and response.body().startswith(b"%PDF")
