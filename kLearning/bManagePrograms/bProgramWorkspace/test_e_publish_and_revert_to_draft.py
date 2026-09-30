import re
from playwright.sync_api import sync_playwright, expect
from utils.learning_helper import (
    open_browser, open_program, main_content, unique_name, create_program, add_root_module,
    publish_program, modal, expect_toast, search_programs, delete_program,
)


def status_badge(page, title):
    search_programs(page, title)
    return main_content(page).locator("article").filter(has_text=title).locator("span").first


def test_publish_and_revert_to_draft():
    with sync_playwright() as p:
        browser, page = open_browser(p)
        main = main_content(page)
        title = unique_name("QA Learning Publish")
        program_id = create_program(page, title, hours="2")
        try:
            # a program without modules can't be published
            open_program(page, program_id, "?tab=settings")
            main.get_by_role("button", name="Publish Program").click()
            modal(page, "Publish Learning Program").get_by_role("button", name="Publish", exact=True).click()
            expect_toast(page, "Publishing failed: Hour allocations are incomplete or mismatched.")

            add_root_module(page, program_id, "QA Publish Module", hours="2")
            publish_program(page, program_id)
            expect(status_badge(page, title)).to_have_text(re.compile("^published$", re.I))

            open_program(page, program_id, "?tab=settings")
            main.get_by_role("button", name="Revert to Draft").click()
            dialog = modal(page, "Revert to Draft")
            expect(dialog).to_contain_text("You must unenroll all users first.")
            dialog.get_by_role("button", name="Revert to Draft").click()
            expect(main.get_by_role("button", name="Publish Program")).to_be_visible()
            expect(status_badge(page, title)).to_have_text(re.compile("^draft$", re.I))
        finally:
            delete_program(page, title)

        browser.close()
