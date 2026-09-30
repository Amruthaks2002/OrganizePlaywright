from playwright.sync_api import sync_playwright, expect
from utils.learning_helper import open_browser, main_content, open_manage_programs


def test_grid_and_list_view():
    with sync_playwright() as p:
        browser, page = open_browser(p)
        open_manage_programs(page)
        main = main_content(page)

        main.get_by_role("button", name="List").click()
        page.wait_for_timeout(1000)
        # list view headers are plain divs, uppercased by CSS
        for column in ["Program", "Hours", "Learners", "Modules", "Completion", "Status"]:
            expect(main.get_by_text(column, exact=True).first).to_be_visible()
        expect(main.locator("article")).to_have_count(0)
        expect(main.get_by_role("link", name="Open program →")).to_have_count(0)

        main.get_by_role("button", name="Grid").click()
        page.wait_for_timeout(1000)
        expect(main.locator("article").first).to_be_visible()
        expect(main.get_by_role("link", name="Open program →").first).to_be_visible()

        browser.close()
