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


# no openpyxl on this machine, so .xlsx is read with the standard library
def xlsx_rows(content):
    """Rows of the first sheet of an .xlsx file as lists of strings."""
    import io, re, zipfile
    from xml.etree import ElementTree
    ns = {"m": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}
    book = zipfile.ZipFile(io.BytesIO(content))
    shared = []
    if "xl/sharedStrings.xml" in book.namelist():
        for item in ElementTree.fromstring(book.read("xl/sharedStrings.xml")).findall("m:si", ns):
            shared.append("".join(t.text or "" for t in item.iter(f"{{{ns['m']}}}t")))
    sheet = sorted(n for n in book.namelist() if n.startswith("xl/worksheets/sheet"))[0]
    rows = []
    for row in ElementTree.fromstring(book.read(sheet)).iter(f"{{{ns['m']}}}row"):
        cells = {}
        for cell in row.findall("m:c", ns):
            column = re.match(r"[A-Z]+", cell.get("r")).group()
            index = 0
            for ch in column:
                index = index * 26 + ord(ch) - 64
            value = cell.find("m:v", ns)
            inline = cell.find("m:is", ns)
            if cell.get("t") == "s" and value is not None:
                text = shared[int(value.text)]
            elif inline is not None:
                text = "".join(t.text or "" for t in inline.iter(f"{{{ns['m']}}}t"))
            else:
                text = value.text if value is not None else ""
            cells[index - 1] = text
        rows.append([cells.get(i, "") for i in range(max(cells) + 1)] if cells else [])
    return rows


def latest_run(hr: Page, statuses=("approved", "paid")):
    """The newest pay run in one of the statuses, or None."""
    for year in range(date.today().year + 1, 2023, -1):
        for run in props_at(hr, f"{PAY_RUNS_URL}?year={year}")["payRuns"]["data"]:
            if run["status"] in statuses:
                return run
    return None


def require_step_up():
    """Profile changes ask for a fresh authenticator code, which only a TOTP secret can produce."""
    if not os.environ.get("PAYROLL_HR_TOTP_SECRET"):
        pytest.skip("saving a payroll profile needs a fresh authenticator code: set PAYROLL_HR_TOTP_SECRET")


def confirm_step_up(page: Page):
    dialog = page.locator("div.fixed:visible").filter(has_text="authenticator").last
    dialog.locator("input").first.fill(totp(os.environ["PAYROLL_HR_TOTP_SECRET"]))
    dialog.get_by_role("button", name="Confirm").click()


IMPORT_HEADERS = ["Employee Number", "Employee Name", "Salary Template Name", "Gross Amount (per annum)",
                  "CTC (per annum)", "B.P Amount", "Dearness Allowance Amount", "HRA Amount", "Special Allowance Amount",
                  "Fixed Allowance", "Performance Bonus", "Is Eligible For PF", "Is Eligible For ESI", "Effective From",
                  "Revision Reason"]


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


def test_bank_advice():
    """PR-227: the bank advice (.xlsx) has one row per employee paid in the run and its amounts add up to the run's
    net pay. Needs PAYROLL_HR_TOTP_SECRET (the download asks for an authenticator code)."""
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=os.environ.get("HEADLESS") == "1")
        hr = open_hr(browser)
        run = latest_run(hr)
        slips = run_payslips(hr, run["id"])

        rows = xlsx_rows(download_with_step_up(hr, f"{BASE_URL}/payroll/pay-runs/{run['id']}", "Bank advice (.xlsx)"))
        assert rows[0] != IMPORT_HEADERS, "the bank advice is the salary import template"
        names = " ".join(" ".join(r) for r in rows)
        assert all(s["user"]["name"] in names for s in slips)
        assert str(run["total_net"]) in names.replace(",", "") or f"{run['total_net']:.2f}" in names

        browser.close()
