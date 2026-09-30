import re
from playwright.sync_api import sync_playwright, expect
from utils.learning_helper import open_browser, main_content, open_manage_programs


def test_open_program():
    with sync_playwright() as p:
        browser, page = open_browser(p)
        open_manage_programs(page)
        main = main_content(page)

        card = main.locator("article").first
        title = card.locator("h3, h2").first.inner_text().strip()
        href = card.get_by_role("link", name="Open program →").get_attribute("href")
        card.get_by_role("link", name="Open program →").click()

        expect(page).to_have_url(href)
        expect(page).to_have_url(re.compile(r"/admin/learning/programs/\d+$"))
        expect(main.get_by_text(title, exact=True).first).to_be_visible()
        expect(main.get_by_text("Program Workspace: overview")).to_be_visible()

        browser.close()
