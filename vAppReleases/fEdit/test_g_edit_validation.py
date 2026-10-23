from playwright.sync_api import sync_playwright
from utils.app_releases_helper import (open_browser, page_props, current_releases, restore_releases,
                                       open_edit_from_card, save_button, submit_expecting_error,
                                       assert_nothing_saved, bump, lower)


def test_edit_validation():
    """AR-036: Save changes follows the publish rules (required, minimum not above latest) and won't take the latest
    below the platform's previous release; the release is left unchanged."""
    with sync_playwright() as p:
        browser, page = open_browser(p)
        snapshot = current_releases(page)
        props = page_props(page)
        total = props["history"]["total"]
        release = snapshot["android"]
        previous = next(r for r in props["history"]["data"]
                        if r["platform"] == "android" and r["id"] != release["id"])["latest_version"]
        try:
            for fields, name, message in [
                ({"latest_version": ""}, "latest_version", "The latest version field is required."),
                ({"min_version": ""}, "min_version", "The min version field is required."),
                ({"min_version": bump(release["latest_version"])}, "min_version",
                 "The minimum version cannot be higher than the latest version."),
                ({"latest_version": lower(previous), "min_version": "0.0.1"}, "latest_version",
                 f"The latest version cannot be lower than the previous {previous}."),
            ]:
                submit_expecting_error(page, save_button(page), name, message,
                                       prepare=lambda: open_edit_from_card(page, "android"), **fields)
            assert_nothing_saved(page, snapshot, total)
        finally:
            restore_releases(page, snapshot)

        browser.close()
