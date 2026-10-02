from playwright.sync_api import sync_playwright, expect
from utils.onboarding_helper import open_browser, open_directory, search_box, status_tab, candidate_rows, candidate_row


def test_filters_from_url():
    """OD-015: search and status in the URL are applied on load (and survive a reload)."""
    with sync_playwright() as p:
        browser, page = open_browser(p)
        open_directory(page, search="maju", status="submitted")

        expect(search_box(page)).to_have_value("maju")
        expect(candidate_row(page, "maju")).to_have_count(1)
        expect(candidate_rows(page)).to_have_count(1)

        page.reload()
        expect(search_box(page)).to_have_value("maju")
        expect(candidate_row(page, "maju")).to_have_count(1)

        browser.close()
