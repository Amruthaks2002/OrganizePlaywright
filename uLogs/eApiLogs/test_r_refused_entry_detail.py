"""API-018: A refused entry.

Steps:
1. Log in as admin and open API Logs over all time filtered to Refused.
2. Open the newest refused entry.

Expected: the row and the page show "refused"; when the entry has an error message, the page shows it, so the
reason for the refusal can be read.
"""
import json
import time
from datetime import date, datetime
from urllib.parse import urlencode
from zoneinfo import ZoneInfo

from playwright.sync_api import sync_playwright, expect
from utils.login_helper import login

BASE_URL = "https://organice.qc.iocod.com"
LOGS_URL = f"{BASE_URL}/api-logs"
EMPTY_MESSAGE = "No API calls match these filters."
SEARCH = "input[placeholder='User name, email or reference']"


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


IST = ZoneInfo("Asia/Kolkata")


def to_ist(created_at):
    return datetime.fromisoformat(created_at.replace("Z", "+00:00")).astimezone(IST)


def display_timestamp(created_at):
    """How the page shows a time, e.g. 12 Nov 2026, 10:07:37 AM (India time)."""
    return to_ist(created_at).strftime("%-d %b %Y, %I:%M:%S %p")


def displayed_date(timestamp):
    return datetime.strptime(timestamp.split(",")[0].strip(), "%d %b %Y").date()


def detail_text(page):
    page.get_by_role("link", name="← Back to API Logs").wait_for(state="visible")
    time.sleep(1)
    return page.locator("main").first.inner_text()


def squash(text):
    return "".join(str(text).split())


def expected_parts(log, labels):
    """What the detail page should show for an entry."""
    parts = [labels.get(log["service_name"], log["service_name"]), display_timestamp(log["created_at"]),
             log.get("user_name") or "—", log.get("actor_name") or "—",
             f"{log['method']} {log['url']}" if log.get("url") else "—",
             str(log["http_status"]) if log.get("http_status") is not None else "—",
             f"{log['duration_ms']} ms" if log.get("duration_ms") is not None else "—",
             log.get("reference") or "—"]
    if log.get("ip"):
        parts.append(f"{log['ip']} · {log.get('user_agent') or ''}".strip())
    return parts


def payload_text(value):
    if value in (None, "", [], {}):
        return "Nothing recorded."
    return value if isinstance(value, str) else json.dumps(value, indent=2, ensure_ascii=False)


def test_api_018_refused_entry_detail():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        login(page)

        logs = props_at(page, list_url(outcome="refused", **all_time()))["apiLogs"]["data"]
        assert logs, "no refused entries"
        assert page.locator("table tbody tr td:nth-child(4)").first.inner_text().strip().lower() == "refused"

        log = props_at(page, f"{LOGS_URL}/{logs[0]['id']}")["apiLog"]
        text = detail_text(page)
        assert "refused" in text.lower(), "the page doesn't say refused"
        if log.get("error"):
            error = log["error"] if isinstance(log["error"], str) else json.dumps(log["error"])
            assert squash(error)[:60] in squash(text), f"the error {error[:80]!r} isn't shown"

        browser.close()
