from playwright.sync_api import sync_playwright, expect
from utils.learning_helper import (
    open_browser, open_program, main_content, unique_name, create_program, add_root_module, delete_program,
)


def test_hours_allocation():
    with sync_playwright() as p:
        browser, page = open_browser(p)
        main = main_content(page)
        title = unique_name("QA Learning Hours")
        program_id = create_program(page, title, hours="5")
        try:
            open_program(page, program_id, "/curriculum")
            allocation = main.get_by_text("Estimated Hours Allocation").locator("xpath=../../..")
            expect(allocation).to_contain_text("0 / 5 hrs")
            expect(allocation).to_contain_text("left")

            add_root_module(page, program_id, "QA Hours Module A", hours="2")
            expect(allocation).to_contain_text("2 /")

            add_root_module(page, program_id, "QA Hours Module B", hours="3")
            expect(allocation).to_contain_text("5 / 5 hrs")
            expect(allocation).to_contain_text("Ready")
        finally:
            delete_program(page, title)

        browser.close()
