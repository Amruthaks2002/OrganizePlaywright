from playwright.sync_api import sync_playwright, expect
from utils.marketplace_helper import (
    open_browser, unique_name, open_create, fill_form, submit_for_review, field_error, delete_apps, CREATE_URL,
)


def test_invalid_url():
    """MP-012: a link that isn't a URL is refused and nothing is created."""
    with sync_playwright() as p:
        browser, page = open_browser(p)
        name = unique_name()
        try:
            open_create(page)
            fill_form(page, name=name, short="Invalid link test.", url="not a url")
            submit_for_review(page)
            expect(field_error(page, "The external url field must be a valid URL.")).to_be_visible()
            assert page.url == CREATE_URL, page.url
        finally:
            delete_apps(page, name)

        browser.close()
