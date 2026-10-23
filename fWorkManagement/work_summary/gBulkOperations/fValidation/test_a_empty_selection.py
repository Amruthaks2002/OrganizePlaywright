from playwright.sync_api import sync_playwright
from utils.work_summary_helper import open_browser, open_hours
from utils.work_summary_bulk_helper import bulk_api, EMPTY_ERROR


def test_empty_selection():
    """WS-083: each bulk endpoint refuses an empty list with 'Please select at least one time log.'"""
    with sync_playwright() as p:
        browser, page = open_browser(p)
        open_hours(page)
        for action in ("approve", "reject", "delete"):
            status, body = bulk_api(page, action, [])
            assert status == 422, (action, status, body)
            assert body["errors"]["time_log_ids"] == [EMPTY_ERROR], (action, body)
        browser.close()
