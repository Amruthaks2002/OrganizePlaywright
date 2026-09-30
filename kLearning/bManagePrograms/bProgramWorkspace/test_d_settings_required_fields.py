from playwright.sync_api import sync_playwright, expect
from utils.learning_helper import (
    open_browser, open_program, main_content, unique_name, create_program, delete_program,
)


def test_settings_required_fields():
    with sync_playwright() as p:
        browser, page = open_browser(p)
        main = main_content(page)
        title = unique_name("QA Learning Required")
        program_id = create_program(page, title, hours="2")
        try:
            open_program(page, program_id, "?tab=settings")
            title_input = main.locator("input[type=text]").first
            hours_input = main.locator("input[type=number]").first

            title_input.fill("")
            main.get_by_role("button", name="Save Changes").click()
            assert title_input.evaluate("e => e.validationMessage") != "", "Expected an empty Title to be rejected"

            title_input.fill(title)
            hours_input.fill("")
            main.get_by_role("button", name="Save Changes").click()
            assert hours_input.evaluate("e => e.validationMessage") != "", "Expected empty Est. Hours to be rejected"

            # nothing was saved
            page.reload()
            expect(title_input).to_have_value(title)
            expect(hours_input).to_have_value("2")
        finally:
            delete_program(page, title)

        browser.close()
