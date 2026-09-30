import re
from playwright.sync_api import sync_playwright, expect
from utils.learning_helper import (
    open_browser, main_content, open_manage_programs, unique_name, modal,
    expect_toast, search_programs, delete_program,
)


def test_create_program():
    with sync_playwright() as p:
        browser, page = open_browser(p)
        open_manage_programs(page)
        main = main_content(page)
        title = unique_name("QA Learning Create")
        try:
            main.get_by_role("button", name="New Program").click()
            dialog = modal(page, "Create new program")
            expect(dialog.get_by_text("Set up the basics — you can add modules later.")).to_be_visible()
            dialog.locator("input[type=text]").fill(title)
            dialog.locator("textarea").fill("QA automation program description")
            dialog.locator("input[type=number]").nth(0).fill("6")
            dialog.locator("input[type=number]").nth(1).fill("3")
            dialog.get_by_role("button", name="Create program").click()
            expect_toast(page, "Learning Program created successfully.")

            search_programs(page, title)
            card = main.locator("article").filter(has_text=title)
            expect(card).to_have_count(1)
            expect(card.locator("span").first).to_have_text(re.compile("^draft$", re.I))
            expect(card.get_by_text("QA automation program description")).to_be_visible()
            expect(card.get_by_text("6.00")).to_be_visible()
        finally:
            delete_program(page, title)

        browser.close()
