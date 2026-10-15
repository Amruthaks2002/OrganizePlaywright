from playwright.sync_api import sync_playwright
from utils.work_summary_helper import open_browser
from utils.work_summary_bulk_helper import (bulk_prefix, create_logs, bulk_api, statuses, cleanup_prefixed, DUPLICATE_ERROR)


def test_duplicate_ids():
    """WS-088: the same id twice in one request is refused as a whole ('has a duplicate value') and the entry is
    left alone. Approve is only sent a duplicated missing id."""
    with sync_playwright() as p:
        browser, page = open_browser(p)
        prefix = bulk_prefix()
        try:
            [log] = create_logs(page, prefix, 1)
            for action, ids in [("reject", [log["id"]] * 2), ("delete", [log["id"]] * 2), ("approve", [999999999] * 2)]:
                status, body = bulk_api(page, action, ids)
                assert status == 422, (action, status, body)
                if action != "approve":
                    assert body["errors"]["time_log_ids.0"] == [DUPLICATE_ERROR], (action, body)
                assert statuses(page, prefix) == {log["description"]: "pending"}, action
        finally:
            cleanup_prefixed(page, prefix)
            browser.close()
