"""ML-024: Mails of the types the older tests don't cover open correctly.

Steps:
1. Log in as admin.
2. For Leave Cancelled, Work Mode Cancelled, Asset Checked Out, Asset Checked In, Test Email, Onboarding
   Invitation, Onboarding Correction, Payslip Published and Bulk Email: load Mail Logs filtered to that type over
   all time and open the newest mail.

Expected: the mail page shows the same subject and "Recipient: <address>" as the row, and the mail body is not
empty. Types with no mails at all (on 2026-11-12: onboarding, payslip, bulk) can't be checked; the test fails only
if none of the types has mails.
"""
import json
import time
from datetime import date
from urllib.parse import urlencode

from playwright.sync_api import sync_playwright, expect
from utils.login_helper import login

BASE_URL = "https://organice.qc.iocod.com"
LOGS_URL = f"{BASE_URL}/mail-logs"
EMPTY_MESSAGE = "No mail has been sent yet."


def page_props(page):
    """Props of a full page load (they go stale after in-page filtering, so only use them right after goto)."""
    props = json.loads(page.locator("[data-page]").first.get_attribute("data-page"))["props"]
    if "filters" in props:
        props["filters"] = props["filters"] or {}  # the app sends [] when nothing is filtered
    return props


def props_at(page, url):
    page.goto(url)
    page.locator("main").first.wait_for(state="visible")
    time.sleep(1)
    return page_props(page)


def list_url(**filters):
    return f"{LOGS_URL}?{urlencode(filters)}"


TYPES = ["leave_cancelled", "work_mode_cancelled", "asset_checked_out", "asset_checked_in", "test_email",
         "onboarding_invitation", "onboarding_correction", "payslip_published", "bulk_email"]


def test_ml_024_other_email_types_open():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        login(page)
        today = date.today().isoformat()

        checked, empty, problems = [], [], []
        for event_type in TYPES:
            mails = props_at(page, list_url(event_type=event_type, start_date="2000-01-01", end_date=today))["mailLogs"]["data"]
            if not mails:
                empty.append(event_type)
                continue
            mail = mails[0]
            href = page.locator("table tbody tr").first.locator("td").nth(1).get_by_role("link").get_attribute("href")
            detail = props_at(page, href)["mailLog"]
            main = page.locator("main").first.inner_text()
            if mail["subject"] not in main:
                problems.append(f"{event_type}: subject {mail['subject']!r} not shown")
            if f"Recipient: {mail['recipient_email']}".replace(" ", "") not in main.replace(" ", ""):
                problems.append(f"{event_type}: recipient {mail['recipient_email']!r} not shown")
            if not (detail.get("body_html") or "").strip():
                problems.append(f"{event_type}: empty body")
            checked.append(event_type)
        print(f"checked {checked}; no mails for {empty}")
        assert checked, f"none of {TYPES} has any mail"
        assert not problems, problems

        browser.close()
