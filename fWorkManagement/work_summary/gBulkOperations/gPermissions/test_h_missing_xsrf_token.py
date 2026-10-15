from playwright.sync_api import sync_playwright
from utils.work_summary_helper import open_browser
from utils.work_summary_bulk_helper import bulk_prefix, create_logs, bulk_api, statuses, cleanup_prefixed


def test_missing_xsrf_token():
    """WS-098: a signed-in admin's bulk request without the XSRF token is refused with 419 and changes nothing.
    Approve is only sent a missing id."""
    with sync_playwright() as p:
        browser, page = open_browser(p)
        prefix = bulk_prefix()
        try:
            [log] = create_logs(page, prefix, 1)
            for action, ids in [("approve", [999999999]), ("reject", [log["id"]]), ("delete", [log["id"]])]:
                status, body = bulk_api(page, action, ids, xsrf=False)
                assert status == 419, (action, status, body)
            assert statuses(page, prefix) == {log["description"]: "pending"}
        finally:
            cleanup_prefixed(page, prefix)
            browser.close()
