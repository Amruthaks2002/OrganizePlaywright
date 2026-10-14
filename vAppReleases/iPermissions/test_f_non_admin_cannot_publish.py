from playwright.sync_api import sync_playwright
from utils.app_releases_helper import (open_browser, open_browser_as, page_props, current_releases, api,
                                       assert_nothing_saved, APP_RELEASES_URL, FIELDS)


def test_non_admin_cannot_publish():
    """AR-055: an employee sending the publish request directly gets 403 and nothing is published."""
    with sync_playwright() as p:
        admin_browser, admin = open_browser(p)
        snapshot = current_releases(admin)
        total = page_props(admin)["history"]["total"]

        browser, page = open_browser_as(p, "employee")
        response = api(page, "POST", APP_RELEASES_URL,
                       {"platform": "android", **{k: snapshot["android"][k] for k in FIELDS},
                        "optional_message": "AR-055 should not save"})
        assert response.status == 403, response.status
        browser.close()

        assert_nothing_saved(admin, snapshot, total)
        admin_browser.close()
