from playwright.sync_api import sync_playwright, expect
from utils.learning_helper import (
    open_browser, open_program, main_content, unique_name, create_program, modal, delete_program,
)


def test_module_required_fields():
    with sync_playwright() as p:
        browser, page = open_browser(p)
        main = main_content(page)
        title = unique_name("QA Learning Module Req")
        program_id = create_program(page, title)
        try:
            open_program(page, program_id, "/curriculum")
            main.get_by_role("button", name="Add Root Module").click()
            dialog = modal(page, "Add Module to Curriculum")
            title_input = dialog.locator("input[type=text]")
            hours_input = dialog.locator("input[type=number]")

            dialog.get_by_role("button", name="Save Node").click()
            assert title_input.evaluate("e => e.validationMessage") != "", "Expected an empty Title to be rejected"

            title_input.fill("QA Module Without Hours")
            hours_input.fill("")
            dialog.get_by_role("button", name="Save Node").click()
            assert hours_input.evaluate("e => e.validationMessage") != "", "Expected empty Estimated Hours to be rejected"

            dialog.get_by_role("button", name="Cancel").click()
            expect(main.get_by_text("No modules added yet.")).to_be_visible()
        finally:
            delete_program(page, title)

        browser.close()
