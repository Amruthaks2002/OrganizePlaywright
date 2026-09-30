from playwright.sync_api import sync_playwright, expect
from utils.learning_helper import (
    open_browser, main_content, unique_name, create_program, add_root_module, modal, select_node,
    delete_program,
)


def test_assessment_required_fields():
    with sync_playwright() as p:
        browser, page = open_browser(p)
        main = main_content(page)
        title = unique_name("QA Learning Assess Req")
        program_id = create_program(page, title, hours="1")
        try:
            add_root_module(page, program_id, "QA Assess Req Module", hours="1")
            select_node(page, "QA Assess Req Module")

            main.get_by_role("button", name="+ Add Assessment").click()
            dialog = modal(page, "Add Assessment")
            title_input = dialog.get_by_placeholder("Title")
            score_input = dialog.locator("input[type=number]")

            dialog.get_by_role("button", name="Create Assessment").click()
            assert title_input.evaluate("e => e.validationMessage") != "", "Expected an empty Title to be rejected"

            title_input.fill("QA Assessment Without Score")
            score_input.fill("")
            dialog.get_by_role("button", name="Create Assessment").click()
            assert score_input.evaluate("e => e.validationMessage") != "", "Expected an empty Max Score to be rejected"

            dialog.get_by_role("button", name="Cancel").click()
            expect(main.get_by_text("No assessments added.")).to_be_visible()
        finally:
            delete_program(page, title)

        browser.close()
