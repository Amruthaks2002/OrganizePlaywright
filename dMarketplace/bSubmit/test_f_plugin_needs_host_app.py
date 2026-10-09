from playwright.sync_api import sync_playwright, expect
from utils.marketplace_helper import (
    open_browser, unique_name, open_create, pick_platform, fill_form, submit_for_review, field_error, delete_apps,
    CREATE_URL,
)


def test_plugin_needs_host_app():
    """MP-015: a plugin can't be submitted without naming the application it runs in."""
    with sync_playwright() as p:
        browser, page = open_browser(p)
        name = unique_name()
        try:
            open_create(page)
            pick_platform(page, "plugin")
            fill_form(page, name=name, short="Plugin without host.", url="https://example.com/plugin")
            submit_for_review(page)
            expect(field_error(page, "Please name the application this plugin runs in.")).to_be_visible()
            assert page.url == CREATE_URL, page.url
        finally:
            delete_apps(page, name)

        browser.close()
