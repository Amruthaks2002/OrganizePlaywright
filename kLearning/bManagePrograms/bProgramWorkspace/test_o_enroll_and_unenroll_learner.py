import re
from playwright.sync_api import sync_playwright, expect
from utils.learning_helper import (
    open_browser, open_program, main_content, unique_name, create_program, add_root_module, publish_program,
    open_enroll_dialog, enroll_learner, modal, expect_toast, cleanup_program,
)


def test_enroll_and_unenroll_learner():
    with sync_playwright() as p:
        browser, page = open_browser(p)
        main = main_content(page)
        title = unique_name("QA Learning Enroll")
        program_id = create_program(page, title, hours="1")
        try:
            add_root_module(page, program_id, "QA Enroll Module", hours="1")

            # a draft program can't be assigned to users
            enroll_learner(page, program_id, "Olivia Davis", "olivia@gmail.com")
            expect_toast(page, "Only published and active learning programs can be assigned to users.")

            publish_program(page, program_id)

            # nothing selected keeps the Enroll button disabled
            dialog = open_enroll_dialog(page, program_id)
            expect(dialog.get_by_role("button", name="Enroll Learners")).to_be_disabled()
            dialog.get_by_role("button", name="Cancel").click()

            enroll_learner(page, program_id, "Olivia Davis", "olivia@gmail.com")
            expect_toast(page, "Successfully enrolled 1 user(s).")
            row = main.locator("tbody tr").filter(has_text="olivia@gmail.com")
            expect(row).to_contain_text(re.compile("not started", re.I))
            expect(row).to_contain_text("QA Enroll Module")

            # a program with learners can't be reverted to draft
            open_program(page, program_id, "?tab=settings")
            main.get_by_role("button", name="Revert to Draft").click()
            modal(page, "Revert to Draft").get_by_role("button", name="Revert to Draft").click()
            expect_toast(page, "Cannot revert to draft: Program has active enrolled users")

            open_program(page, program_id, "/learners")
            main.locator("tbody tr").filter(has_text="olivia@gmail.com").get_by_role("button", name="Unenroll").click()
            dialog = modal(page, "Unenroll Learner")
            expect(dialog).to_contain_text("Are you sure you want to unenroll Olivia Davis?")
            dialog.get_by_role("button", name="Unenroll", exact=True).click()
            expect_toast(page, "User unenrolled and progress cleared successfully.")
            expect(main.get_by_text("No learners enrolled matching the filters.")).to_be_visible()
        finally:
            cleanup_program(page, title, program_id)

        browser.close()
