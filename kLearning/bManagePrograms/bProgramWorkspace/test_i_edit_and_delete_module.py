from playwright.sync_api import sync_playwright, expect
from utils.learning_helper import (
    open_browser, main_content, unique_name, create_program, add_root_module, modal, expect_toast,
    select_node, delete_program,
)


def test_edit_and_delete_module():
    with sync_playwright() as p:
        browser, page = open_browser(p)
        main = main_content(page)
        title = unique_name("QA Learning Edit Module")
        program_id = create_program(page, title, hours="1")
        try:
            add_root_module(page, program_id, "QA Module Original", hours="1")
            select_node(page, "QA Module Original")

            main.get_by_role("button", name="✏️").first.click()
            dialog = modal(page, "Edit Module Settings")
            expect(dialog.locator("input[type=text]")).to_have_value("QA Module Original")
            dialog.locator("input[type=text]").fill("QA Module Renamed")
            dialog.get_by_role("button", name="Save Node").click()
            expect_toast(page, "Learning Node updated successfully.")
            expect(main.get_by_text("QA Module Renamed", exact=True).first).to_be_visible()
            expect(main.get_by_text("QA Module Original", exact=True)).to_have_count(0)

            # the delete asks for a native confirm, which open_browser accepts
            main.locator("button[title='Delete Node']").first.click()
            expect_toast(page, "Learning Node deleted successfully.")
            expect(main.get_by_text("No modules added yet.")).to_be_visible()
        finally:
            delete_program(page, title)

        browser.close()
