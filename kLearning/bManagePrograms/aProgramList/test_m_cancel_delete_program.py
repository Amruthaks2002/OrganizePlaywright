from playwright.sync_api import sync_playwright, expect
from utils.learning_helper import (
    open_browser, main_content, unique_name, create_program, search_programs, modal, delete_program,
)


def test_cancel_delete_program():
    with sync_playwright() as p:
        browser, page = open_browser(p)
        main = main_content(page)
        title = unique_name("QA Learning Keep")
        create_program(page, title)
        try:
            search_programs(page, title)
            main.locator("article").filter(has_text=title).locator("button[aria-label=Delete]").click(force=True)
            dialog = modal(page, "Delete Learning Program")
            dialog.get_by_role("button", name="Cancel").click()
            expect(page.get_by_text("Delete Learning Program")).to_have_count(0)

            search_programs(page, title)
            expect(main.locator("article").filter(has_text=title)).to_have_count(1)
        finally:
            delete_program(page, title)

        browser.close()
