import re
from playwright.sync_api import sync_playwright, expect
from utils.onboarding_helper import (
    open_browser, open_onboarding_submenu, main_content, search_box, status_tab, STATUS_TABS, candidate_rows,
)


def test_page_loads():
    """OD-001: Onboarding > Directory opens the candidate directory with its header, tabs, search and table."""
    with sync_playwright() as p:
        browser, page = open_browser(p)
        open_onboarding_submenu(page, "directory")
        main = main_content(page)

        expect(page).to_have_url(re.compile(r"/hr/onboarding$"))
        expect(main.get_by_role("heading", name="Employee Onboarding Directory")).to_be_visible()
        expect(main.get_by_text("Manage and review conversational onboarding details")).to_be_visible()
        expect(main.get_by_role("link", name="Field Config")).to_be_visible()
        expect(main.get_by_role("button", name="Add Candidate")).to_be_visible()
        expect(search_box(page)).to_be_visible()
        for tab in ["All", *STATUS_TABS]:
            expect(status_tab(page, tab)).to_be_visible()
        for column in ["CANDIDATE DETAIL", "CONTACT INFO", "ROLE & JOINING", "REVIEW STATUS", "LAST ACTIVITY", "ACTIONS"]:
            expect(main.locator("thead")).to_contain_text(column, ignore_case=True)
        expect(candidate_rows(page).first).to_be_visible()

        browser.close()
