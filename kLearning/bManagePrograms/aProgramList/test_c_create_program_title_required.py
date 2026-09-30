from playwright.sync_api import sync_playwright, expect
from utils.learning_helper import open_browser, main_content, open_manage_programs, modal


def test_create_program_title_required():
    with sync_playwright() as p:
        browser, page = open_browser(p)
        open_manage_programs(page)
        main = main_content(page)
        before = main.locator("article").count()

        main.get_by_role("button", name="New Program").click()
        dialog = modal(page, "Create new program")
        dialog.locator("textarea").fill("Program without a title")
        dialog.get_by_role("button", name="Create program").click()

        title_input = dialog.locator("input[type=text]")
        assert title_input.evaluate("e => e.validationMessage") != "", "Expected the empty Title to be rejected"
        expect(dialog).to_be_visible()

        dialog.get_by_role("button", name="Cancel").click()
        expect(main.locator("article")).to_have_count(before)

        browser.close()
