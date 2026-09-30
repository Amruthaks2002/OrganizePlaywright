from playwright.sync_api import sync_playwright, expect
from utils.learning_helper import (
    open_browser, main_content, unique_name, create_program, search_programs, modal, expect_toast,
)


def test_delete_program():
    with sync_playwright() as p:
        browser, page = open_browser(p)
        main = main_content(page)
        title = unique_name("QA Learning Delete")
        create_program(page, title)

        search_programs(page, title)
        main.locator("article").filter(has_text=title).locator("button[aria-label=Delete]").click(force=True)
        dialog = modal(page, "Delete Learning Program")
        expect(dialog).to_contain_text(f"Are you sure you want to delete {title}?")
        dialog.get_by_role("button", name="Delete", exact=True).click()
        expect_toast(page, "Learning Program deleted successfully.")

        search_programs(page, title)
        expect(main.get_by_text("No programs found")).to_be_visible()

        browser.close()
