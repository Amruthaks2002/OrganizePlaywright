from playwright.sync_api import sync_playwright
from utils.marketplace_helper import open_browser, unique_name, create_app, delete_apps, api, app_data


def test_approve_draft_refused():
    """MP-028: a draft the author never submitted can't be approved.

    Known bug: POST /marketplace/{id}/approve publishes a draft straight away (status becomes
    approved, history shows only 'Approved by Admin User'), so an unfinished app goes live without
    its author ever submitting it. This test fails until approve only accepts pending submissions."""
    with sync_playwright() as p:
        browser, page = open_browser(p)
        name = unique_name()
        try:
            app_id = create_app(page, name, submit=False)
            api(page, "POST", f"/marketplace/{app_id}/approve")

            data = app_data(page, name)
            assert data["status"] == "draft", f"draft was published by approve: status is {data['status']}"
        finally:
            delete_apps(page, name)

        browser.close()
