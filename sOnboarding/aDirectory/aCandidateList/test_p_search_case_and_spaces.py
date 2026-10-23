from playwright.sync_api import sync_playwright, expect
from utils.onboarding_helper import open_browser, open_directory, candidate_row


def test_search_case_and_spaces():
    """OD-016: search ignores case and surrounding spaces."""
    with sync_playwright() as p:
        browser, page = open_browser(p)

        open_directory(page, search="MAJU")
        expect(candidate_row(page, "maju")).to_have_count(1)

        open_directory(page, search="  maju  ")
        expect(candidate_row(page, "maju")).to_have_count(1)

        browser.close()
