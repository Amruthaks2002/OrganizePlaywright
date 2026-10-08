from playwright.sync_api import sync_playwright
from utils.events_helper import open_browser, bulk_post, BULK_DELETE

# far beyond any real event id
MISSING_ID = 99999999


def test_endpoint_validation():
    """EB-016: the bulk-delete endpoint refuses an empty selection and an event that doesn't exist."""
    with sync_playwright() as p:
        browser, page = open_browser(p)

        status, body = bulk_post(page, BULK_DELETE, {"ids": []})
        assert status == 422, f"empty: expected 422, got {status} {body}"
        assert body["errors"]["ids"] == ["The ids field is required."], body

        status, body = bulk_post(page, BULK_DELETE, {"ids": [MISSING_ID]})
        assert status == 422, f"missing id: expected 422, got {status} {body}"
        assert body["errors"]["ids.0"] == ["The selected ids.0 is invalid."], body

        browser.close()
