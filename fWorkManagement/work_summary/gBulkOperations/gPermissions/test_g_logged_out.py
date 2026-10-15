import os
from playwright.sync_api import sync_playwright
from utils.work_summary_helper import open_browser, BASE_URL
from utils.work_summary_bulk_helper import (bulk_prefix, create_logs, statuses, BULK_URL, _xsrf, cleanup_prefixed)


def test_logged_out():
    """WS-097: without signing in, every bulk endpoint redirects to the login page and changes nothing.
    Approve is only sent a missing id."""
    with sync_playwright() as p:
        admin_browser, admin = open_browser(p)
        browser = p.chromium.launch(headless=os.environ.get("HEADLESS") == "1")
        anon = browser.new_page()
        prefix = bulk_prefix()
        try:
            [log] = create_logs(admin, prefix, 1)
            anon.goto(BASE_URL)  # picks up an XSRF cookie, so the request gets past the CSRF check
            for action, ids in [("approve", [999999999]), ("reject", [log["id"]]), ("delete", [log["id"]])]:
                response = anon.request.post(f"{BULK_URL}{action}", data={"time_log_ids": ids},
                                             headers={"X-XSRF-TOKEN": _xsrf(anon)}, max_redirects=0)
                assert response.status == 302 and response.headers["location"].endswith("/login"), \
                    (action, response.status, response.headers.get("location"))
            assert statuses(admin, prefix) == {log["description"]: "pending"}
        finally:
            cleanup_prefixed(admin, prefix)
            browser.close()
            admin_browser.close()
