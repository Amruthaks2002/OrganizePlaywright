from playwright.sync_api import sync_playwright
from utils.app_usage_helper import open_browser, open_app_usage, install_rows, search_installs


def test_search_by_device():
    """AI-005: the search box says "Name, email, device or version", so searching the text shown in an
    install's Device column finds that install.

    Known bug: the Device column shows the device model (often "—") and below it the OS build
    (e.g. QP1A.190711.020), but searching the OS build finds nothing, so nothing visible under Device can
    be searched. This test fails until that's fixed."""
    with sync_playwright() as p:
        browser, page = open_browser(p)
        open_app_usage(page)
        target = install_rows(page)[0]
        device_texts = [t for t in target["device"] if t != "—"]
        assert device_texts, target

        for term in device_texts:
            search_installs(page, term)
            emails = [r["email"] for r in install_rows(page)]
            assert target["email"] in emails, f"searching device text {term!r} found {emails}"

        browser.close()
