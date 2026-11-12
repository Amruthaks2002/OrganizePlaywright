"""ML-022: Each row shows the right recipient, subject, event, status and time.

Steps:
1. Log in as admin and open Mail Logs over the year up to yesterday.
2. Compare every row on the first page with the mail behind it.

Expected: Recipient = the first address (plus "+N more" when there are N others), Subject = the mail subject (a link
to its page), Event = the event type's label, Status = the status, Sent At = the send time in India time
("11 Nov, 2026, 04:23 PM").
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


def table_rows(page):
    """Visible mail rows as dicts (the empty state has a single cell and is skipped)."""
    rows = []
    for row in page.locator("table tbody tr").all():
        cells = row.locator("td")
        if cells.count() != 5:
            continue
        rows.append({
            "recipient": cells.nth(0).inner_text().strip(),
            "subject": cells.nth(1).inner_text().strip(),
            "event": cells.nth(2).inner_text().strip(),
            "status": cells.nth(3).inner_text().strip(),
            "sent_at": cells.nth(4).inner_text().strip(),
        })
    return rows


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


def test_ml_022_row_content_matches_data():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        login(page)
        start, end = wide_range()

        props = props_at(page, list_url(start_date=start, end_date=end))
        labels = {t["value"]: t["label"] for t in props["eventTypes"]}
        mails = props["mailLogs"]["data"]
        rows = table_rows(page)
        assert rows and len(rows) == len(mails)
        problems = []
        for index, (mail, row) in enumerate(zip(mails, rows)):
            recipients = [r.strip() for r in mail["recipient_email"].split(",") if r.strip()]
            recipient = recipients[0] + (f"+{len(recipients) - 1} more" if len(recipients) > 1 else "")
            expected = {"recipient": recipient, "subject": mail["subject"], "event": labels.get(mail["event_type"]),
                        "status": mail["status"], "sent_at": display_timestamp(mail["sent_at"])}
            for key, value in expected.items():
                if row[key].replace(" ", "") != str(value).replace(" ", ""):
                    problems.append(f"{mail['id']} {key}: shows {row[key]!r}, expected {value!r}")
            link = page.locator("table tbody tr").nth(index).locator("td").nth(1).get_by_role("link")
            if not (link.get_attribute("href") or "").endswith(f"/mail-logs/{mail['id']}"):
                problems.append(f"{mail['id']} subject links to {link.get_attribute('href')}")
        assert not problems, problems

        browser.close()
