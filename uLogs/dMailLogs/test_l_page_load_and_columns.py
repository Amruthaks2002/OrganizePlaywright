"""ML-012: Opening the page by URL, the sidebar, columns, page size and order.

Steps:
1. Log in as admin and go straight to /mail-logs.

Expected:
- The "Mail Logs" heading, the Type / Status / From Date / To Date filters and Reset are shown.
- Logs > Mail Log is shown and highlighted in the sidebar, no other Logs item is.
- Columns, in order: Recipient, Subject, Event, Status, Sent At.
- At most 15 rows a page, newest first.
"""
import json
import time
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


def type_select(page):
    return page.locator("main select").first


def status_select(page):
    return page.locator("main select").last


ACTIVE = "bg-slate-100"


def test_ml_012_page_load_and_columns():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        login(page)

        props = props_at(page, LOGS_URL)
        expect(page.get_by_role("heading", name="Mail Logs")).to_be_visible()
        expect(type_select(page)).to_be_visible()
        expect(status_select(page)).to_be_visible()
        assert page.locator("input[type='date']").count() == 2
        expect(page.get_by_role("button", name="Reset")).to_be_visible()

        link = page.get_by_test_id("sidebar-child-mail-log")
        expect(link).to_be_visible()
        assert ACTIVE in (link.get_attribute("class") or ""), "Mail Log is not highlighted in the sidebar"
        for other in ["audit-log", "leave-audit-logs", "work-mode-logs", "api-log", "log-viewer"]:
            item = page.get_by_test_id(f"sidebar-child-{other}")
            if item.count():
                assert ACTIVE not in (item.get_attribute("class") or "").split(), f"{other} is also highlighted"

        headers = [h.strip().upper() for h in page.locator("table thead th").all_inner_texts()]
        assert headers == ["RECIPIENT", "SUBJECT", "EVENT", "STATUS", "SENT AT"], headers

        mails = props["mailLogs"]["data"]
        assert props["mailLogs"]["per_page"] == 15 and len(mails) <= 15
        assert len(table_rows(page)) == len(mails)
        sent = [m["sent_at"] for m in mails]
        assert sent == sorted(sent, reverse=True), "rows are not newest first"

        browser.close()
