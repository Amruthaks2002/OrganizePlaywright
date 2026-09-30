import re
from playwright.sync_api import sync_playwright, expect
from utils.learning_helper import open_browser, main_content, open_manage_programs, unique_name, create_program, delete_program


def test_search_programs():
    with sync_playwright() as p:
        browser, page = open_browser(p)
        main = main_content(page)
        title = unique_name("QA Learning Search")
        create_program(page, title)
        try:
            open_manage_programs(page)
            main.get_by_placeholder("Search programs...").fill(title)
            page.wait_for_timeout(2000)
            expect(page).to_have_url(re.compile(r"search="))
            cards = main.locator("article")
            expect(cards).to_have_count(1)
            expect(cards.first).to_contain_text(title)
        finally:
            delete_program(page, title)

        browser.close()
