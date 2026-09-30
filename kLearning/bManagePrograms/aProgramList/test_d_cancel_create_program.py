from playwright.sync_api import sync_playwright, expect
from utils.learning_helper import (
    open_browser, main_content, open_manage_programs, unique_name, modal, search_programs,
)


def test_cancel_create_program():
    with sync_playwright() as p:
        browser, page = open_browser(p)
        open_manage_programs(page)
        main = main_content(page)
        title = unique_name("QA Learning Cancel")

        main.get_by_role("button", name="New Program").click()
        dialog = modal(page, "Create new program")
        dialog.locator("input[type=text]").fill(title)
        dialog.get_by_role("button", name="Cancel").click()
        expect(page.get_by_text("Create new program")).to_have_count(0)

        search_programs(page, title)
        expect(main.get_by_text("No programs found")).to_be_visible()

        browser.close()
