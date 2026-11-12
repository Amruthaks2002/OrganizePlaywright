"""ML-025: The mail page shows whether the mail was sent.

Steps:
1. Log in as admin and open Mail Logs filtered to Failed over the year up to yesterday.
2. Open the newest failed mail.

Expected: besides subject and recipient, the mail page shows its status ("failed") and when it was sent
(e.g. "11 Nov, 2026, 04:23 PM"), so a failed mail can be recognised without going back to the list.

Known gap: the mail page only shows the subject, recipient and body. This test fails until status and send time
are shown (drop it if that's by design).
"""
import json
import time
from datetime import date, datetime, timedelta
from urllib.parse import urlencode
from zoneinfo import ZoneInfo

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


def wide_range():
    """The year up to yesterday: ending yesterday so mails being sent right now don't shift the rows."""
    today = date.today()
    return (today - timedelta(days=365)).isoformat(), (today - timedelta(days=1)).isoformat()


IST = ZoneInfo("Asia/Kolkata")


def to_ist(sent_at):
    return datetime.fromisoformat(sent_at.replace("Z", "+00:00")).astimezone(IST)


def display_timestamp(sent_at):
    """How the page shows a time, e.g. 11 Nov, 2026, 04:23 PM (India time)."""
    return to_ist(sent_at).strftime("%-d %b, %Y, %I:%M %p")


def displayed_date(timestamp):
    return datetime.strptime(",".join(timestamp.split(",")[:2]).strip(), "%d %b, %Y").date()


def test_ml_025_detail_shows_status():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        login(page)
        start, end = wide_range()

        mails = props_at(page, list_url(status="failed", start_date=start, end_date=end))["mailLogs"]["data"]
        assert mails, "no failed mails in the year up to yesterday"
        page.locator("table tbody tr").first.locator("td").nth(1).get_by_role("link").click()
        page.get_by_role("link", name="← Back to Mail Activity Logs").wait_for(state="visible")
        time.sleep(1)

        header = page.locator("main").first.inner_text().split("Note:")[0]
        missing = []
        if "failed" not in header.lower():
            missing.append("status 'failed'")
        if display_timestamp(mails[0]["sent_at"]) not in header:
            missing.append(f"sent time {display_timestamp(mails[0]['sent_at'])}")
        assert not missing, f"the mail page doesn't show {missing}"

        browser.close()
