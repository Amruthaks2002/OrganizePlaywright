"""ML-023: The "+N more" recipients popup.

Steps:
1. Log in as admin and open Mail Logs filtered to Leave Submitted over the year up to yesterday (these go to
   several HR addresses).
2. Click "+N more" on the first row, check the popup, close it with Close.
3. Open it again and close it with Esc.

Expected: N is the number of other recipients; the "Recipients" popup lists every address of the mail; Close and
Esc both close it.
"""
import json
import time
from datetime import date, timedelta
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


def wide_range():
    """The year up to yesterday: ending yesterday so mails being sent right now don't shift the rows."""
    today = date.today()
    return (today - timedelta(days=365)).isoformat(), (today - timedelta(days=1)).isoformat()


def popup(page):
    return page.locator("div.fixed.inset-0.z-50").filter(has_text="Recipients").last


def test_ml_023_more_recipients_popup():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        login(page)
        start, end = wide_range()

        mails = props_at(page, list_url(event_type="leave_submitted", start_date=start, end_date=end))["mailLogs"]["data"]
        index = next((i for i, m in enumerate(mails) if "," in m["recipient_email"]), None)
        assert index is not None, "no Leave Submitted mail with several recipients"
        recipients = [r.strip() for r in mails[index]["recipient_email"].split(",") if r.strip()]
        button = page.locator("table tbody tr").nth(index).get_by_role("button", name=f"+{len(recipients) - 1} more")
        expect(button).to_be_visible()

        button.click()
        expect(popup(page)).to_be_visible()
        listed = popup(page).inner_text()
        missing = [r for r in recipients if r not in listed]
        assert not missing, f"the popup doesn't list {missing}"
        popup(page).get_by_role("button", name="Close").click()
        expect(popup(page)).to_be_hidden()

        button.click()
        expect(popup(page)).to_be_visible()
        page.keyboard.press("Escape")
        expect(popup(page)).to_be_hidden()

        browser.close()
