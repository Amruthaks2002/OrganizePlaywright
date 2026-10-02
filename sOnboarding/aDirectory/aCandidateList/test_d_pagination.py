import re
from playwright.sync_api import sync_playwright, expect
from utils.onboarding_helper import open_browser, open_directory, main_content, candidate_rows, settle


def test_pagination():
    """OD-004: the directory is paginated 10 per page; page 2 shows different candidates."""
    with sync_playwright() as p:
        browser, page = open_browser(p)
        open_directory(page)
        expect(candidate_rows(page)).to_have_count(10)
        first_page = candidate_rows(page).all_inner_texts()

        main_content(page).get_by_role("link", name="2", exact=True).click()
        expect(page).to_have_url(re.compile(r"page=2"))
        settle(page)
        expect(candidate_rows(page).first).to_be_visible()
        second_page = candidate_rows(page).all_inner_texts()
        assert not set(first_page) & set(second_page), "page 2 repeats candidates from page 1"

        browser.close()
