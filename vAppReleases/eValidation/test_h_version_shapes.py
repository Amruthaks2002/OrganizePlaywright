from playwright.sync_api import sync_playwright
from utils.app_releases_helper import (open_browser, page_props, current_releases, api, assert_nothing_saved,
                                       APP_RELEASES_URL, FIELDS, VERSION_FORMAT)

ACCEPTED = ["3", "3.0", "3.0.0.1", "03.0.0"]
REFUSED = ["v3.0.0", "3.0.0-beta", "3..0", "abc", "3.0.0 x"]


def test_version_shapes():
    """AR-027: a version is one or more dot-separated numbers; prefixes, suffixes and empty parts are refused.
    Each request also carries a 501-character message, so the server always refuses it and nothing is saved; the
    errors show whether the version itself passed."""
    with sync_playwright() as p:
        browser, page = open_browser(p)
        snapshot = current_releases(page)
        total = page_props(page)["history"]["total"]
        base = {"platform": "android", **{k: snapshot["android"][k] for k in FIELDS}, "mandatory_message": "x" * 501}

        for version in ACCEPTED + REFUSED:
            for name in ["latest_version", "min_version"]:
                response = api(page, "POST", APP_RELEASES_URL, {**base, name: version})
                assert response.status == 422, (version, name, response.status)
                errors = response.json()["errors"]
                assert "mandatory_message" in errors, errors
                expected = None if version in ACCEPTED else [VERSION_FORMAT]
                assert errors.get(name) == expected, (version, name, errors)

        assert_nothing_saved(page, snapshot, total)

        browser.close()
