import re
from playwright.sync_api import sync_playwright, expect
from utils.learning_helper import (
    open_browser, main_content, open_manage_programs, unique_name, create_program, add_root_module,
    publish_program, enroll_learner, expect_toast, cleanup_program,
)


def choose_learner(page, name):
    main = main_content(page)
    main.get_by_placeholder("All learners").click()
    main.get_by_placeholder("All learners").fill(name)
    page.get_by_role("option", name=name, exact=True).click()
    page.wait_for_timeout(2000)


def test_filter_by_learner():
    with sync_playwright() as p:
        browser, page = open_browser(p)
        main = main_content(page)
        title = unique_name("QA Learning Learner Filter")
        program_id = create_program(page, title, hours="1")
        try:
            add_root_module(page, program_id, "QA Filter Module", hours="1")
            publish_program(page, program_id)
            enroll_learner(page, program_id, "Olivia Davis", "olivia@gmail.com")
            expect_toast(page, "Successfully enrolled 1 user(s).")

            open_manage_programs(page)
            main.get_by_placeholder("Search programs...").fill(title)
            page.wait_for_timeout(1500)

            # the program shows for the enrolled learner...
            choose_learner(page, "Olivia Davis")
            expect(page).to_have_url(re.compile(r"user_id=\d+"))
            expect(main.locator("article").filter(has_text=title)).to_have_count(1)

            # ...and not for a learner who isn't enrolled in it
            main.locator("[aria-label='Clear Selected']").first.click(force=True)
            choose_learner(page, "Swathi")
            expect(main.locator("article").filter(has_text=title)).to_have_count(0)
        finally:
            cleanup_program(page, title, program_id)

        browser.close()
