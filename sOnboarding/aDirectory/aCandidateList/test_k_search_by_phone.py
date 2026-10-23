import re
from playwright.sync_api import sync_playwright, expect
from utils.onboarding_helper import open_browser, open_directory, search_box, candidate_rows, candidate_row, settle


def test_search_by_phone():
    """OD-011: searching by phone number finds the candidate and puts the search in the URL."""
    with sync_playwright() as p:
        browser, page = open_browser(p)
        open_directory(page)

        search_box(page).fill("7878789999")
        expect(page).to_have_url(re.compile(r"search=7878789999"))
        settle(page)
        expect(candidate_row(page, "maju")).to_have_count(1)
        expect(candidate_rows(page)).to_have_count(1)

        browser.close()
