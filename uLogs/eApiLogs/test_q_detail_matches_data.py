"""API-017: The entry page matches the stored entry, for every service.

Steps:
1. Log in as admin.
2. For each service (ATS · User Sync, Open ATS (Sign-in), Open Organice (Sign-in from ATS)) open its newest entry.

Expected: the page shows the service, outcome, time, user, triggered by, "<METHOD> <URL>", HTTP status, duration,
reference, "<IP> · <browser>", the SENT payload and the RECEIVED response ("Nothing recorded." when empty), all
matching the stored entry ("—" for empty values).
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


def test_api_017_detail_matches_data():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        login(page)
        services = props_at(page, LOGS_URL)["services"]
        labels = {s["value"]: s["label"] for s in services}

        problems, checked = [], []
        for service in services:
            logs = props_at(page, list_url(service_name=service["value"], **all_time()))["apiLogs"]["data"]
            if not logs:
                continue
            log = props_at(page, f"{LOGS_URL}/{logs[0]['id']}")["apiLog"]
            text = detail_text(page)
            flat = squash(text)
            for part in expected_parts(log, labels) + [log["outcome"]]:
                if squash(part).lower() not in flat.lower():
                    problems.append(f"{service['value']}: {part!r} not shown")
            for title, value in [("SENT", log.get("payload")), ("RECEIVED", log.get("response"))]:
                if squash(payload_text(value)) not in flat:
                    problems.append(f"{service['value']}: {title} doesn't show {payload_text(value)[:80]!r}")
            checked.append(service["value"])
        assert checked, "no entries at all"
        assert not problems, problems

        browser.close()
