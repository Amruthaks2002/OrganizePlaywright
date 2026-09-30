from playwright.sync_api import sync_playwright, expect
from utils.learning_helper import (
    BASE_URL, goto, open_browser, main_content, unique_name, create_program, add_root_module,
    publish_program, enroll_learner, expect_toast, cleanup_program,
)


def test_enrolled_program_shows_on_dashboard():
    with sync_playwright() as p:
        browser, page = open_browser(p)
        main = main_content(page)
        title = unique_name("QA Learning Dashboard")
        program_id = create_program(page, title, hours="2")
        try:
            add_root_module(page, program_id, "QA Dashboard Module", hours="2")
            publish_program(page, program_id)
            enroll_learner(page, program_id, "Admin User", "admin@example.com")
            expect_toast(page, "Successfully enrolled 1 user(s).")

            goto(page, f"{BASE_URL}/learning/dashboard")
            card = main.locator("div").filter(has_text=title).filter(has_text="Start Journey").last
            expect(card).to_be_visible()
            expect(card.get_by_text("Not Started")).to_be_visible()
            expect(card.get_by_text("Current: QA Dashboard Module")).to_be_visible()
            expect(card.get_by_role("link", name="Start Journey")).to_have_attribute(
                "href", f"{BASE_URL}/learning/programs/{program_id}"
            )
        finally:
            cleanup_program(page, title, program_id)

        # once unenrolled, the dashboard goes back to the empty state
        goto(page, f"{BASE_URL}/learning/dashboard")
        expect(main.get_by_text(title)).to_have_count(0)

        browser.close()
