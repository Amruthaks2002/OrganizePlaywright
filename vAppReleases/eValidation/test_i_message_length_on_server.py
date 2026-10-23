from playwright.sync_api import sync_playwright
from utils.app_releases_helper import (open_browser, page_props, current_releases, api, assert_nothing_saved,
                                       APP_RELEASES_URL, FIELDS)


def test_message_length_on_server():
    """AR-028: the server refuses a message over 500 characters even when the form's limit is bypassed."""
    with sync_playwright() as p:
        browser, page = open_browser(p)
        snapshot = current_releases(page)
        total = page_props(page)["history"]["total"]
        base = {"platform": "android", **{k: snapshot["android"][k] for k in FIELDS}}

        for name, label in [("optional_message", "optional"), ("mandatory_message", "mandatory")]:
            response = api(page, "POST", APP_RELEASES_URL, {**base, name: "x" * 501})
            assert response.status == 422, (name, response.status)
            assert response.json()["errors"] == {
                name: [f"The {label} message field must not be greater than 500 characters."]}

        assert_nothing_saved(page, snapshot, total)

        browser.close()
