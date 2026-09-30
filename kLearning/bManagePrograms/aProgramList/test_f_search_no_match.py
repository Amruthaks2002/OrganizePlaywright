from playwright.sync_api import sync_playwright, expect
from utils.learning_helper import open_browser, main_content, open_manage_programs


def test_search_no_match():
    with sync_playwright() as p:
        browser, page = open_browser(p)
        open_manage_programs(page)
        main = main_content(page)

        main.get_by_placeholder("Search programs...").fill("zzz-no-such-program-qa")
        page.wait_for_timeout(2000)
        expect(main.get_by_text("No programs found")).to_be_visible()
        expect(main.get_by_text("No learning programs matched your search criteria. Try adjusting your filters.")).to_be_visible()
        expect(main.locator("article")).to_have_count(0)

        main.get_by_role("button", name="Clear filters").click()
        page.wait_for_timeout(2000)
        expect(main.locator("article").first).to_be_visible()
        expect(main.get_by_placeholder("Search programs...")).to_have_value("")

        browser.close()
