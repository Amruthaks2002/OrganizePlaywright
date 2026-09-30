import re
from playwright.sync_api import sync_playwright, expect
from utils.learning_helper import (
    open_browser, open_program, main_content, unique_name, create_program, add_root_module, publish_program,
    enroll_learner, expect_toast, cleanup_program,
)


def test_search_and_filter_learners():
    with sync_playwright() as p:
        browser, page = open_browser(p)
        main = main_content(page)
        title = unique_name("QA Learning Learners")
        program_id = create_program(page, title, hours="1")
        try:
            add_root_module(page, program_id, "QA Learners Module", hours="1")
            publish_program(page, program_id)
            enroll_learner(page, program_id, "Olivia Davis", "olivia@gmail.com")
            expect_toast(page, "Successfully enrolled 1 user(s).")
            enroll_learner(page, program_id, "David", "david@iocod.com")
            expect_toast(page, "Successfully enrolled 1 user(s).")

            open_program(page, program_id, "/learners")
            rows = main.locator("tbody tr")
            expect(rows).to_have_count(2)

            search = main.get_by_placeholder("Search by name or email...")
            search.fill("olivia@gmail.com")
            expect(page).to_have_url(re.compile(r"search=olivia"))
            expect(rows).to_have_count(1)
            expect(rows.first).to_contain_text("Olivia Davis")

            search.fill("zzz-no-such-learner")
            expect(main.get_by_text("No learners enrolled matching the filters.")).to_be_visible()
            search.fill("")

            status = main.locator("select")
            status.select_option(label="Not Started")
            expect(page).to_have_url(re.compile(r"status=not_started|status=not"))
            expect(rows).to_have_count(2)
            status.select_option(label="Completed")
            expect(main.get_by_text("No learners enrolled matching the filters.")).to_be_visible()
            status.select_option(label="All Statuses")
            expect(rows).to_have_count(2)
        finally:
            cleanup_program(page, title, program_id)

        browser.close()
