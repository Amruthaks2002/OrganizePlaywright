import re
from playwright.sync_api import sync_playwright, expect
from utils.learning_helper import (
    open_browser, open_program, main_content, unique_name, create_program, add_root_module,
    modal, expect_toast, delete_program,
)


def test_quick_actions():
    with sync_playwright() as p:
        browser, page = open_browser(p)
        main = main_content(page)
        title = unique_name("QA Learning Quick Actions")
        program_id = create_program(page, title, hours="1")
        try:
            actions = {
                "Create Module": r"/curriculum$",
                "Assign Learners": r"/learners$",
                "Review Assignments": r"/assignments$",
            }
            for action, url in actions.items():
                open_program(page, program_id)
                main.get_by_role("link", name=action).click()
                expect(page).to_have_url(re.compile(url))

            # a draft program also offers "Publish Program" from the overview
            add_root_module(page, program_id, "QA Quick Module", hours="1")
            open_program(page, program_id)
            main.get_by_role("button", name="Publish Program").click()
            dialog = modal(page, "Publish Learning Program")
            expect(dialog).to_contain_text("Are you sure you want to publish this learning program?")
            dialog.get_by_role("button", name="Publish Program").click()
            expect_toast(page, "Learning Program published successfully.")
            page.reload()
            expect(main.get_by_role("button", name="Publish Program")).to_have_count(0)
        finally:
            delete_program(page, title)

        browser.close()
