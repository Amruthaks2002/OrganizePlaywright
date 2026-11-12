"""API-019: Entry pages never show secrets.

Steps:
1. Log in as admin and open the newest entry of each service, plus the newest refused entry.
2. Check the page text and the data sent to the browser.

Expected: no signature, secret, password, API key value, bearer token or Authorization header appears; only key
ids, timestamps and token claims are shown.
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


SECRET = re.compile(r'(authorization|bearer\s+[a-z0-9._-]{10,}|"?(secret|password|signature|api[_-]?key|private[_-]?key|token)"?\s*[:=])', re.I)


def test_api_019_no_secrets_shown():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        login(page)
        services = props_at(page, LOGS_URL)["services"]

        ids = []
        for service in services:
            logs = props_at(page, list_url(service_name=service["value"], start_date="2000-01-01",
                                           end_date=time.strftime("%Y-%m-%d")))["apiLogs"]["data"]
            ids += [log["id"] for log in logs[:2]]
        refused = props_at(page, list_url(outcome="refused", start_date="2000-01-01",
                                          end_date=time.strftime("%Y-%m-%d")))["apiLogs"]["data"]
        ids += [log["id"] for log in refused[:1]]
        assert ids, "no entries at all"

        problems = []
        for log_id in ids:
            log = props_at(page, f"{LOGS_URL}/{log_id}")["apiLog"]
            for where, text in [("page", page.locator("main").first.inner_text()),
                                ("data", json.dumps({k: log.get(k) for k in ("payload", "response", "error", "url")}))]:
                match = SECRET.search(text)
                if match:
                    problems.append(f"{log_id} {where}: {text[max(0, match.start() - 30):match.end() + 30]!r}")
        assert not problems, problems

        browser.close()
