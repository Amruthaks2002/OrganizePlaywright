from playwright.sync_api import sync_playwright, expect
from utils.learning_helper import (
    open_browser, open_program, main_content, unique_name, create_program, add_root_module, modal,
    select_node, delete_program,
)


def test_import_dialogs():
    with sync_playwright() as p:
        browser, page = open_browser(p)
        main = main_content(page)
        title = unique_name("QA Learning Import")
        program_id = create_program(page, title, hours="1")
        try:
            add_root_module(page, program_id, "QA Import Module", hours="1")

            open_program(page, program_id, "/curriculum")
            main.get_by_role("button", name="Import Excel ⚡").click()
            dialog = modal(page, "Import Curriculum Structure")
            expect(dialog.get_by_text("Excel Import Template")).to_be_visible()
            expect(dialog.get_by_text("Download Template File (.xlsx) →")).to_be_visible()
            expect(dialog.get_by_text("Supports .xlsx and .xls (Max 5MB)")).to_be_visible()
            expect(dialog.locator("input[type=file]")).to_have_count(1)
            dialog.get_by_role("button", name="Cancel").click()
            expect(page.get_by_text("Import Curriculum Structure")).to_have_count(0)

            select_node(page, "QA Import Module")
            main.get_by_role("button", name="⚡ Bulk Import").click()
            dialog = modal(page, "Bulk Import Materials: QA Import Module")
            expect(dialog.get_by_text("Import External Links")).to_be_visible()
            expect(dialog.get_by_text("Upload Files in Bulk")).to_be_visible()
            dialog.get_by_role("button", name="Cancel").click()
            expect(page.get_by_text("Bulk Import Materials: QA Import Module")).to_have_count(0)
            expect(main.get_by_text("No materials added.")).to_be_visible()
        finally:
            delete_program(page, title)

        browser.close()
