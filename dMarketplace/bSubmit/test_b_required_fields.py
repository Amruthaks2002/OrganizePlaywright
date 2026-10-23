from playwright.sync_api import sync_playwright, expect
from utils.marketplace_helper import open_browser, open_create, submit_for_review, field_error, expect_toast, CREATE_URL


def test_required_fields():
    """MP-011: submitting the empty form keeps you on it, with errors for name, short description
    and the website link."""
    with sync_playwright() as p:
        browser, page = open_browser(p)
        open_create(page)

        submit_for_review(page)
        expect_toast(page, "The name field is required.")
        for message in ["The name field is required.", "The short description field is required.",
                        "A link is required for this delivery method."]:
            expect(field_error(page, message)).to_be_visible()
        assert page.url == CREATE_URL, page.url

        browser.close()
