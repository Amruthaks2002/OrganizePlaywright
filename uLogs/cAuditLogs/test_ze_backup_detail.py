"""AL-032: Audit History of a backup record.

Steps:
1. Open Audit Logs filtered to Model = system_backup.
2. Click View on the first row.

Expected: Audit History lists that backup's records (at least the one clicked), not "No audit records found for
this entity".

Known bug: backup rows open an empty Audit History ("No audit records found for this entity.", "Showing 0 audit
record(s)"). This test fails until that's fixed.
"""
import json
import time
from urllib.parse import urlencode

from playwright.sync_api import sync_playwright, expect
from utils.login_helper import login

BASE_URL = "https://organice.qc.iocod.com"
LOGS_URL = f"{BASE_URL}/audits"
SUBTITLE = "Track all system changes and user activities"
EMPTY_MESSAGE = "No audit logs found"


def page_props(page):
    """Props of a full page load (they go stale after in-page filtering, so only use them right after goto)."""
    return json.loads(page.locator("[data-page]").first.get_attribute("data-page"))["props"]


def props_at(page, url, wait_for=SUBTITLE):
    page.goto(url)
    page.get_by_text(wait_for).first.wait_for(state="visible")
    return page_props(page)


def list_url(**filters):
    return f"{LOGS_URL}?{urlencode(filters)}"


def open_detail(page, row_index=0):
    """Clicks View on a row and returns the props of the Audit History it loads."""
    with page.expect_response(lambda r: "/audits/entity" in r.url) as info:
        page.locator("table tbody tr").nth(row_index).get_by_role("button", name="View").click()
    page.get_by_role("heading", name="Audit History").wait_for(state="visible")
    time.sleep(1)
    return info.value.json()["props"]


def report_cards(page):
    return page.locator("div.rounded-lg.border.overflow-hidden")


def shown(value):
    """How the detail page shows a stored value: '-' for empty."""
    return "-" if value is None or value == "" else str(value)


def test_al_032_backup_detail():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        login(page)

        audits = props_at(page, list_url(model="system_backup"))["audits"]["data"]
        assert audits, "no backup records"
        props = open_detail(page)
        assert props["audits"], f"Audit History of backup {props['entity']['auditable_id']} is empty"
        assert audits[0]["id"] in [a["id"] for a in props["audits"]]
        expect(page.get_by_text("No audit records found for this entity.")).to_be_hidden()

        browser.close()
