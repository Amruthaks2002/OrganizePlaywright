from playwright.sync_api import sync_playwright, expect
from utils.learning_helper import (
    open_browser, open_program, main_content, unique_name, create_program, expect_toast, delete_program,
)


def test_edit_program_settings():
    with sync_playwright() as p:
        browser, page = open_browser(p)
        main = main_content(page)
        title = unique_name("QA Learning Settings")
        new_title = title + " Edited"
        program_id = create_program(page, title, description="Original description", hours="2")
        try:
            open_program(page, program_id, "?tab=settings")

            main.locator("input[type=text]").first.fill(new_title)
            main.locator("input[type=number]").first.fill("7")
            main.locator("textarea").first.fill("Edited description")
            main.get_by_role("button", name="Save Changes").click()
            expect_toast(page, "Learning Program updated successfully.")

            page.reload()
            expect(main.locator("input[type=text]").first).to_have_value(new_title)
            expect(main.locator("input[type=number]").first).to_have_value("7")
            expect(main.locator("textarea").first).to_have_value("Edited description")
        finally:
            delete_program(page, title)  # also matches the edited title

        browser.close()
