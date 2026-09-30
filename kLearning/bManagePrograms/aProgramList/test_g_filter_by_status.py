import re
from playwright.sync_api import sync_playwright, expect
from utils.learning_helper import open_browser, main_content, open_manage_programs


def test_filter_by_status():
    with sync_playwright() as p:
        browser, page = open_browser(p)
        open_manage_programs(page)
        main = main_content(page)

        for status in ["draft", "published", "archived"]:
            main.get_by_placeholder("Any status").click()
            page.get_by_role("option", name=status, exact=True).click()
            page.wait_for_timeout(2000)
            expect(page).to_have_url(re.compile(f"status={status}"))

            cards = main.locator("article")
            if cards.count() == 0:
                expect(main.get_by_text("No programs found")).to_be_visible()
            for i in range(cards.count()):
                badge = cards.nth(i).locator("span").first
                expect(badge).to_have_text(re.compile(f"^{status}$", re.I))

            main.get_by_role("button", name="Reset").click()
            page.wait_for_timeout(1500)

        browser.close()
