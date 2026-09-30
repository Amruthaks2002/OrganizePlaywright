from playwright.sync_api import sync_playwright, expect
from utils.learning_helper import open_browser, main_content, open_manage_programs


def test_programs_page_loads():
    with sync_playwright() as p:
        browser, page = open_browser(p)
        open_manage_programs(page)
        main = main_content(page)

        expect(main.get_by_text("Learning Programs", exact=True)).to_be_visible()
        expect(main.get_by_text("Create, manage, and monitor learning journeys across your organization.")).to_be_visible()
        expect(main.get_by_role("button", name="New Program")).to_be_visible()
        expect(main.get_by_placeholder("Search programs...")).to_be_visible()
        expect(main.get_by_placeholder("All learners")).to_be_visible()
        expect(main.get_by_placeholder("Any status")).to_be_visible()
        expect(main.get_by_role("button", name="Reset")).to_be_visible()
        expect(main.get_by_role("button", name="Grid")).to_be_visible()
        expect(main.get_by_role("button", name="List")).to_be_visible()
        expect(main.locator("article").first).to_be_visible()
        expect(main.get_by_role("link", name="2", exact=True)).to_be_visible()

        browser.close()
