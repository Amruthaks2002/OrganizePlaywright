from playwright.sync_api import sync_playwright, expect
from utils.asset_helper import (
    open_browser, open_browser_as, unique_prefix, create_assets, delete_assets, open_assets, asset_row, row_id,
    row_holder, bulk_post, BULK_ENDPOINTS,
)

# Ajith PT's user id, so check-out / transfer payloads are otherwise valid
EMPLOYEE_ID = 13


def test_endpoints_forbidden():
    """BS-031: employees and team leads calling the bulk endpoints directly get 403, and the asset
    is left untouched."""
    with sync_playwright() as p:
        browser, page = open_browser(p)
        prefix = unique_prefix()
        try:
            names = create_assets(page, prefix, 1)
            open_assets(page, search=prefix)
            asset_id = row_id(asset_row(page, names[0]))

            for role in ["employee", "team-lead"]:
                role_browser, role_page = open_browser_as(p, role)
                for path in BULK_ENDPOINTS:
                    status, body = bulk_post(role_page, path, {"asset_ids": [asset_id], "user_id": EMPLOYEE_ID})
                    assert status == 403, f"{role} {path}: expected 403, got {status} {body}"
                role_browser.close()

            open_assets(page, search=prefix)
            expect(asset_row(page, names[0])).to_have_count(1)
            expect(row_holder(asset_row(page, names[0]))).to_have_text("Unassigned")
        finally:
            delete_assets(page, prefix)

        browser.close()
