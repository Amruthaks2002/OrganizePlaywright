from playwright.sync_api import sync_playwright, expect
from utils.learning_helper import (
    open_browser, open_program, main_content, unique_name, create_program, modal, expect_toast,
    select_node, delete_program,
)


def test_add_root_module():
    with sync_playwright() as p:
        browser, page = open_browser(p)
        main = main_content(page)
        title = unique_name("QA Learning Module")
        program_id = create_program(page, title, hours="3")
        try:
            open_program(page, program_id, "/curriculum")
            expect(main.get_by_text("No modules added yet.")).to_be_visible()

            main.get_by_role("button", name="Add Root Module").click()
            dialog = modal(page, "Add Module to Curriculum")
            dialog.locator("input[type=text]").fill("QA Root Module")
            dialog.locator("textarea").fill("QA module description")
            dialog.get_by_role("button", name="View Material").click()
            dialog.locator("input[type=number]").fill("3")
            dialog.get_by_role("button", name="Save Node").click()
            expect_toast(page, "Learning Node created successfully.")

            expect(main.get_by_text("QA Root Module", exact=True).first).to_be_visible()
            expect(main.get_by_text("3.00h").first).to_be_visible()
            select_node(page, "QA Root Module")
            expect(main.get_by_text("QA module description")).to_be_visible()
        finally:
            delete_program(page, title)

        browser.close()
