from playwright.sync_api import sync_playwright
from utils.marketplace_helper import (
    open_browser, unique_name, create_live_app, delete_apps, api, open_app, history,
)


def test_approve_twice_refused():
    """MP-029: approving an app that's already live doesn't approve it again.
    Open the review queue (/marketplace/review) in two tabs. 
    Your app should appear in both.
    Tab 1: click Approve on the app. You should see "…is now live in the marketplace".
    Tab 2: don't refresh. Click Approve on the same app.
    Go to the app's detail page and look at the History section."""
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
