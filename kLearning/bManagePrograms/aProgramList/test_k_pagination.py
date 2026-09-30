from playwright.sync_api import sync_playwright, expect
from utils.learning_helper import open_browser, main_content, open_manage_programs


def test_pagination():
    with sync_playwright() as p:
        browser, page = open_browser(p)
        open_manage_programs(page)
        main = main_content(page)
        first_page_titles = main.locator("article h3, article h2").all_inner_texts()

        main.get_by_role("link", name="2", exact=True).click()
        page.wait_for_url("**page=2**")
        page.wait_for_timeout(1500)
        second_page_titles = main.locator("article h3, article h2").all_inner_texts()

        assert second_page_titles, "Expected programs on page 2"
        assert first_page_titles != second_page_titles, "Expected page 2 to list different programs"

        browser.close()
