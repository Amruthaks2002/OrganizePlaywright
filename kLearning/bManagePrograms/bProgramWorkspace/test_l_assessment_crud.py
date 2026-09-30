from playwright.sync_api import sync_playwright, expect
from utils.learning_helper import (
    open_browser, main_content, unique_name, create_program, add_root_module, modal, expect_toast,
    select_node, delete_program,
)


def test_assessment_crud():
    with sync_playwright() as p:
        browser, page = open_browser(p)
        main = main_content(page)
        title = unique_name("QA Learning Assessment")
        program_id = create_program(page, title, hours="1")
        try:
            add_root_module(page, program_id, "QA Assessment Module", hours="1")
            select_node(page, "QA Assessment Module")
            expect(main.get_by_text("No assessments added.")).to_be_visible()

            main.get_by_role("button", name="+ Add Assessment").click()
            dialog = modal(page, "Add Assessment")
            dialog.get_by_placeholder("Title").fill("QA Assignment")
            dialog.get_by_placeholder("Description").fill("QA assignment description")
            dialog.get_by_role("button", name="Assignment", exact=True).click()
            dialog.get_by_placeholder("Write the questions/prompts here").fill("Describe your setup.")
            dialog.locator("input[type=number]").fill("50")
            dialog.get_by_role("button", name="Create Assessment").click()
            expect_toast(page, "Assessment added successfully.")
            expect(main.locator("li").filter(has_text="QA Assignment (assignment)")).to_have_count(1)

            main.locator("li").filter(has_text="QA Assignment").locator("button[title='Edit assessment']").click()
            dialog = modal(page, "Edit Assessment")
            expect(dialog.locator("input[type=number]")).to_have_value("50")
            dialog.get_by_placeholder("Title").fill("QA Assignment Edited")
            dialog.get_by_role("button", name="Save Changes").click()
            expect_toast(page, "Assessment updated successfully.")
            expect(main.locator("li").filter(has_text="QA Assignment Edited")).to_have_count(1)

            main.locator("li").filter(has_text="QA Assignment Edited").locator("button[title='Delete assessment']").click()
            expect_toast(page, "Assessment deleted successfully.")
            expect(main.get_by_text("No assessments added.")).to_be_visible()
        finally:
            delete_program(page, title)

        browser.close()
