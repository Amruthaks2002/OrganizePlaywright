from playwright.sync_api import sync_playwright, expect
from utils.learning_helper import open_browser, main_content, open_manage_programs


def test_reset_filters():
    with sync_playwright() as p:
        browser, page = open_browser(p)
        open_manage_programs(page)
        main = main_content(page)
        total_first_page = main.locator("article").count()

        main.get_by_placeholder("Search programs...").fill("zzz-no-such-program-qa")
        main.get_by_placeholder("Any status").click()
        page.get_by_role("option", name="draft", exact=True).click()
        page.wait_for_timeout(2000)
        expect(main.locator("article")).to_have_count(0)

        main.get_by_role("button", name="Reset").click()
        page.wait_for_timeout(2000)
        expect(main.get_by_placeholder("Search programs...")).to_have_value("")
        expect(main.get_by_text("draft", exact=True)).to_have_count(0)
        expect(main.locator("article")).to_have_count(total_first_page)

        browser.close()
