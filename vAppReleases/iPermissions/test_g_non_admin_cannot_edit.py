from playwright.sync_api import sync_playwright
from utils.app_releases_helper import (open_browser, open_browser_as, page_props, current_releases, api,
                                       assert_nothing_saved, APP_RELEASES_URL, FIELDS)


def test_non_admin_cannot_edit():
    """AR-056: an employee sending the edit request for the current release directly gets 403 and it's unchanged."""
    with sync_playwright() as p:
        admin_browser, admin = open_browser(p)
        snapshot = current_releases(admin)
        total = page_props(admin)["history"]["total"]
        release = snapshot["android"]

        browser, page = open_browser_as(p, "employee")
        response = api(page, "PUT", f"{APP_RELEASES_URL}/{release['id']}",
                       {**{k: release[k] for k in FIELDS}, "optional_message": "AR-056 should not save"})
        assert response.status == 403, response.status
        browser.close()

        assert_nothing_saved(admin, snapshot, total)
        admin_browser.close()
