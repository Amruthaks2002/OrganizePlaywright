from playwright.sync_api import sync_playwright, expect
from utils.learning_helper import (
    open_browser, open_program, main_content, unique_name, create_program, add_root_module, select_node, modal,
    expect_toast, delete_program,
)


def add_assignment(page, module, name):
    main = main_content(page)
    select_node(page, module)
    main.get_by_role("button", name="+ Add Assessment").click()
    dialog = modal(page, "Add Assessment")
    dialog.get_by_placeholder("Title").fill(name)
    dialog.locator("input[type=number]").fill("100")
    dialog.get_by_role("button", name="Create Assessment").click()
    expect_toast(page, "Assessment added successfully.")


def test_filter_assignments():
    with sync_playwright() as p:
        browser, page = open_browser(p)
        main = main_content(page)
        title = unique_name("QA Learning Assignments")
        program_id = create_program(page, title, hours="2")
        try:
            add_root_module(page, program_id, "QA Module One", hours="1")
            add_root_module(page, program_id, "QA Module Two", hours="1")
            add_assignment(page, "QA Module One", "QA Task Alpha")
            add_assignment(page, "QA Module Two", "QA Task Beta")

            open_program(page, program_id, "/assignments")
            rows = main.locator("tbody tr")
            expect(rows).to_have_count(2)
            expect(main.get_by_text("TOTAL ASSESSMENTS").locator("xpath=..")).to_contain_text("2")

            main.locator("select").select_option(label="QA Module Two")
            expect(rows).to_have_count(1)
            expect(rows.first).to_contain_text("QA Task Beta")

            main.get_by_role("button", name="Reset").click()
            expect(rows).to_have_count(2)

            main.get_by_placeholder("Search assignments...").fill("Alpha")
            expect(rows).to_have_count(1)
            expect(rows.first).to_contain_text("QA Task Alpha")
            expect(rows.first).to_contain_text("QA Module One")
        finally:
            delete_program(page, title)

        browser.close()
