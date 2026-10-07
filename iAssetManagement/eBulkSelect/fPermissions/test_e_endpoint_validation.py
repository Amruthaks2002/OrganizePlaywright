from playwright.sync_api import sync_playwright
from utils.asset_helper import open_browser, bulk_post, BULK_ENDPOINTS

# far beyond any real asset id
MISSING_ID = 99999999


def test_endpoint_validation():
    """BS-033: the bulk endpoints refuse an empty selection and an asset that no longer exists,
    even for an admin."""
    with sync_playwright() as p:
        browser, page = open_browser(p)

        for path in BULK_ENDPOINTS:
            status, body = bulk_post(page, path, {"asset_ids": []})
            assert status == 422, f"{path} empty: expected 422, got {status} {body}"
            assert body["errors"]["asset_ids"] == ["Please select at least one asset."], body

            status, body = bulk_post(page, path, {"asset_ids": [MISSING_ID]})
            assert status == 422, f"{path} missing id: expected 422, got {status} {body}"
            assert body["errors"]["asset_ids.0"] == ["One of the selected assets no longer exists."], body

        browser.close()
