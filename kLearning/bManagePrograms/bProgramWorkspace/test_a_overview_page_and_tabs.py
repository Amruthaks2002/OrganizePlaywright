import re
from playwright.sync_api import sync_playwright, expect
from utils.learning_helper import (
    open_browser, open_program, main_content, unique_name, create_program, delete_program,
)


def test_overview_page_and_tabs():
    with sync_playwright() as p:
        browser, page = open_browser(p)
        main = main_content(page)
        title = unique_name("QA Learning Overview")
        program_id = create_program(page, title, description="QA overview description", hours="2")
        try:
            open_program(page, program_id)
            expect(main.get_by_text(title, exact=True).first).to_be_visible()
            expect(main.get_by_text("Program Workspace: overview")).to_be_visible()
            for heading in ["ENROLLED EMPLOYEES", "COMPLETION RATE", "PENDING SUBMISSIONS",
                            "LEARNERS NEEDING ATTENTION", "QUICK ACTIONS", "MODULE PERFORMANCE",
                            "RECENT ACTIVITY", "ABOUT THIS PROGRAM"]:
                # headings are uppercased by CSS, so match case-insensitively
                expect(main.get_by_text(re.compile(f"^{heading}$", re.I))).to_be_visible()
            expect(main.get_by_text("No recent activity")).to_be_visible()
            expect(main.get_by_text("QA overview description")).to_be_visible()

            tabs = {
                "Curriculum": r"/curriculum$",
                "Learners": r"/learners$",
                "Assignments": r"/assignments$",
                "Settings": r"\?tab=settings$",
                "Overview": rf"/programs/{program_id}$",
            }
            for tab, url in tabs.items():
                main.get_by_role("link", name=tab, exact=True).click()
                expect(page).to_have_url(re.compile(url))
                expect(main.get_by_text(f"Program Workspace: {tab.lower()}")).to_be_visible()

            main.get_by_role("link", name="Back to Dashboard").click()
            expect(page).to_have_url(re.compile(r"/admin/learning$"))
        finally:
            delete_program(page, title)

        browser.close()
