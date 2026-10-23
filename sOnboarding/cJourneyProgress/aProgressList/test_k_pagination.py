import re
from playwright.sync_api import sync_playwright, expect
from utils.onboarding_helper import open_browser, open_progress, main_content, progress_rows, settle


def test_pagination():
    """JP-011: the list is paginated 10 per page; page 2 shows different employees."""
    with sync_playwright() as p:
        browser, page = open_browser(p)
        open_progress(page)
        first_page = progress_rows(page).all_inner_texts()

        main_content(page).get_by_role("link", name="2", exact=True).click()
        expect(page).to_have_url(re.compile(r"page=2"))
        settle(page)
        expect(progress_rows(page).first).to_be_visible()
        assert not set(first_page) & set(progress_rows(page).all_inner_texts()), "page 2 repeats employees from page 1"

        browser.close()
