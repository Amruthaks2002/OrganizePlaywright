from playwright.sync_api import sync_playwright, expect
from utils.marketplace_helper import (
    open_browser, open_create, fill_form, submit_for_review, field_error, search_app_names, CREATE_URL,
)


def test_length_limits():
    """MP-014: a name or short description longer than 255 characters is refused."""
    with sync_playwright() as p:
        browser, page = open_browser(p)
        name = "QA App long " + "n" * 250

        open_create(page)
        fill_form(page, name=name, short="s" * 256, url="https://example.com/long")
        submit_for_review(page)
        expect(field_error(page, "The name field must not be greater than 255 characters.")).to_be_visible()
        expect(field_error(page, "The short description field must not be greater than 255 characters.")).to_be_visible()
        assert page.url == CREATE_URL, page.url
        assert search_app_names(page, "QA App long nnnn", mine=True) == []

        browser.close()
