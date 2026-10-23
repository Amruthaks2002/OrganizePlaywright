from playwright.sync_api import sync_playwright
from utils.app_releases_helper import (open_browser, open_releases, page_props, api, current_ids,
                                       assert_nothing_saved, APP_RELEASES_URL, FIELDS)


def test_older_release_locked():
    """AR-037: an older (non-current) release can't be edited even by a direct request: 403, and nothing changes."""
    with sync_playwright() as p:
        browser, page = open_browser(p)
        open_releases(page)
        props = page_props(page)
        old = next(r for r in props["history"]["data"] if r["id"] not in current_ids(props))

        response = api(page, "PUT", f"{APP_RELEASES_URL}/{old['id']}",
                       {**{k: old[k] for k in FIELDS}, "optional_message": "AR-037 should not save"})
        assert response.status == 403, response.status

        assert_nothing_saved(page, props["current"], props["history"]["total"])
        open_releases(page)
        assert next(r for r in page_props(page)["history"]["data"] if r["id"] == old["id"]) == old

        browser.close()
