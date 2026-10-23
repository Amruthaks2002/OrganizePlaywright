from playwright.sync_api import sync_playwright
from utils.marketplace_helper import (
    open_browser, unique_name, create_live_app, delete_apps, api, open_app, history,
)


def test_approve_twice_refused():
    """MP-029: approving an app that's already live doesn't approve it again.

    Known bug: a second POST /marketplace/{id}/approve on an approved app is accepted and adds a
    duplicate 'Approved by Admin User' entry to its history. This test fails until approve only
    accepts pending submissions."""
    with sync_playwright() as p:
        browser, page = open_browser(p)
        name = unique_name()
        try:
            app_id = create_live_app(page, name)
            api(page, "POST", f"/marketplace/{app_id}/approve")

            open_app(page, name)
            assert history(page) == ["Approved by Admin User", "Submitted by Admin User"], history(page)
        finally:
            delete_apps(page, name)

        browser.close()
