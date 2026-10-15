from playwright.sync_api import sync_playwright
from utils.work_summary_helper import open_browser
from utils.work_summary_bulk_helper import (bulk_prefix, create_logs, bulk_api, statuses, cleanup_prefixed, MISSING_ERROR,
                                            NOT_INTEGER_ERROR)

MISSING_ID = 999999999


def test_invalid_ids():
    """WS-084: ids that don't exist, aren't numbers or are null are refused with a 422, and a list mixing a real
    entry with a missing one changes nothing at all (no partial reject / delete). Approve is only sent ids that
    can't be approved."""
    with sync_playwright() as p:
        browser, page = open_browser(p)
        prefix = bulk_prefix()
        try:
            [log] = create_logs(page, prefix, 1)
            for action in ("approve", "reject", "delete"):
                status, body = bulk_api(page, action, [MISSING_ID])
                assert (status, body["errors"]) == (422, {"time_log_ids.0": [MISSING_ERROR]}), (action, status, body)
                status, body = bulk_api(page, action, ["abc"])
                assert (status, body["errors"]) == (422, {"time_log_ids.0": [NOT_INTEGER_ERROR]}), (action, status, body)
                status, body = bulk_api(page, action, [None])
                assert status == 422 and "time_log_ids.0" in body["errors"], (action, status, body)

            for action in ("reject", "delete"):
                status, body = bulk_api(page, action, [log["id"], MISSING_ID])
                assert (status, body["errors"]) == (422, {"time_log_ids.1": [MISSING_ERROR]}), (action, status, body)
                assert statuses(page, prefix) == {log["description"]: "pending"}, action
        finally:
            cleanup_prefixed(page, prefix)
            browser.close()
