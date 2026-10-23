from playwright.sync_api import sync_playwright, expect
from utils.onboarding_helper import open_browser, open_directory, status_tab, candidate_row, directory_empty_state, settle


def test_search_with_tab():
    """OD-014: search and status tab combine - the Submitted "maju" isn't listed under Approved."""
    with sync_playwright() as p:
        browser, page = open_browser(p)
        open_directory(page, search="maju")
        expect(candidate_row(page, "maju")).to_have_count(1)

        status_tab(page, "Approved").click()
        expect(directory_empty_state(page)).to_be_visible()
        expect(candidate_row(page, "maju")).to_have_count(0)

        status_tab(page, "Submitted (Needs Review)").click()
        settle(page)
        expect(candidate_row(page, "maju")).to_have_count(1)

        browser.close()
