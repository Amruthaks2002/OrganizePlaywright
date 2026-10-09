from playwright.sync_api import sync_playwright, expect
from utils.marketplace_helper import (
    open_browser, unique_name, create_live_app, open_create, fill_form, submit_for_review, field_error,
    search_app_names, delete_apps, CREATE_URL,
)


def test_duplicate_name():
    """MP-013: a name that's already in the marketplace is refused, so only one app has it."""
    with sync_playwright() as p:
        browser, page = open_browser(p)
        name = unique_name()
        try:
            create_live_app(page, name)
            open_create(page)
            fill_form(page, name=name, short="Duplicate name test.", url="https://example.com/duplicate")
            submit_for_review(page)
            expect(field_error(page, "An app with this name already exists in the marketplace.")).to_be_visible()
            assert page.url == CREATE_URL, page.url
            assert search_app_names(page, name, mine=True) == [name], search_app_names(page, name, mine=True)
        finally:
            delete_apps(page, name)

        browser.close()
