"""API-001: Heading, filters, columns and the results line.

Steps:
1. Log in as admin and open Logs > API Log from the sidebar.

Expected:
- The "API Logs" heading; the Search box (placeholder "User name, email or reference"), Service, Outcome,
  From Date, To Date and Reset.
- Columns, in order: Time, Service, User, Outcome, HTTP, Duration, Triggered By, Reference.
- The line under the table reads "Showing <from> – <to> of <total> results" and matches the data.
"""
import json
import re
import time
from datetime import date
from urllib.parse import urlencode

from playwright.sync_api import sync_playwright, expect
from utils.login_helper import login

BASE_URL = "https://organice.qc.iocod.com"
LOGS_URL = f"{BASE_URL}/api-logs"
EMPTY_MESSAGE = "No API calls match these filters."
SEARCH = "input[placeholder='User name, email or reference']"


def wait_for_list(page):
    page.get_by_role("heading", name="API Logs").wait_for(state="visible")
    time.sleep(1)


def open_api_logs(page):
    """Logs in as admin and opens Logs > API Log from the sidebar (Logs sits in the collapsed System section)."""
    login(page)
    page.get_by_test_id("sidebar-navigation").wait_for(state="visible")
    if not page.get_by_test_id("sidebar-parent-logs").is_visible():
        page.get_by_test_id("sidebar-section-system").dispatch_event("click")
    link = page.get_by_test_id("sidebar-child-api-log")
    if not link.is_visible():
        page.get_by_test_id("sidebar-parent-logs").click()
    link.wait_for(state="visible")
    link.click()
    wait_for_list(page)


def page_props(page):
    """Props of a full page load (they go stale after in-page filtering, so only use them right after goto)."""
    return json.loads(page.locator("[data-page]").first.get_attribute("data-page"))["props"]


def props_at(page, url):
    page.goto(url)
    page.locator("main").first.wait_for(state="visible")
    time.sleep(1)
    return page_props(page)


def list_url(**filters):
    return f"{LOGS_URL}?{urlencode(filters)}"


def all_time():
    return {"start_date": "2000-01-01", "end_date": date.today().isoformat()}


COLUMNS = ["time", "service", "user", "outcome", "http", "duration", "triggered_by", "reference"]


def table_rows(page):
    """Visible API log rows as dicts (the empty state has a single cell and is skipped)."""
    rows = []
    for row in page.locator("table tbody tr").all():
        cells = row.locator("td")
        if cells.count() != len(COLUMNS):
            continue
        rows.append({key: cells.nth(i).inner_text().strip() for i, key in enumerate(COLUMNS)})
    return rows


def service_select(page):
    return page.locator("main select").first


def outcome_select(page):
    return page.locator("main select").last


def test_api_001_page_load_and_columns():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        open_api_logs(page)

        expect(page.get_by_role("heading", name="API Logs")).to_be_visible()
        expect(page.locator(SEARCH)).to_be_visible()
        expect(service_select(page)).to_be_visible()
        expect(outcome_select(page)).to_be_visible()
        assert page.locator("input[type='date']").count() == 2
        expect(page.get_by_role("button", name="Reset")).to_be_visible()

        headers = [h.strip().upper() for h in page.locator("table thead th").all_inner_texts()]
        assert headers == ["TIME", "SERVICE", "USER", "OUTCOME", "HTTP", "DURATION", "TRIGGERED BY", "REFERENCE"], headers

        logs = props_at(page, page.url)["apiLogs"]
        if logs["total"]:
            line = page.get_by_text(re.compile(r"^Showing .* results$"))
            expect(line).to_have_text(f"Showing {logs['from']} – {logs['to']} of {logs['total']} results")
        else:
            expect(page.get_by_text(EMPTY_MESSAGE)).to_be_visible()

        browser.close()
