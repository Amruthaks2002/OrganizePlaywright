from playwright.sync_api import sync_playwright, expect
from utils.learning_helper import (
    open_browser, open_program, main_content, unique_name, create_program, modal, delete_program,
)


def test_transfer_ownership():
    with sync_playwright() as p:
        browser, page = open_browser(p)
        main = main_content(page)
        title = unique_name("QA Learning Owner")
        program_id = create_program(page, title)
        try:
            open_program(page, program_id, "?tab=settings")
            # the creator owns a new program
            expect(main.get_by_text("Currently owned by Admin User")).to_be_visible()

            owner = main.locator("input[type=search]").first
            owner.click(force=True)
            owner.fill("Olivia")
            page.get_by_role("option", name="Olivia Davis").first.click()
            main.get_by_role("button", name="Transfer Ownership").click()
            dialog = modal(page, "Transfer Program Ownership")
            expect(dialog).to_contain_text(f'transfer ownership of "{title}" to Olivia Davis?')
            dialog.get_by_role("button", name="Transfer", exact=True).click()

            page.wait_for_timeout(1500)
            page.reload()
            expect(main.get_by_text("Currently owned by Olivia Davis")).to_be_visible()
        finally:
            delete_program(page, title)

        browser.close()
