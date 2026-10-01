from playwright.sync_api import sync_playwright, expect
from utils.leave_policy_helper import (
    open_browser, open_leave_policies, policy_names, detail_name, detail_header,
    employees_section, main_content,
)


def test_first_policy_selected_by_default():
    """LP-003: the first policy is selected on load and its details are shown."""
    with sync_playwright() as p:
        browser, page = open_browser(p)
        open_leave_policies(page)
        main = main_content(page)

        expect(detail_name(page)).to_have_text(policy_names(page)[0])
        expect(detail_header(page).get_by_role("button", name="Edit", exact=True)).to_be_visible()
        expect(detail_header(page).get_by_role("button", name="Delete", exact=True)).to_be_visible()
        expect(employees_section(page)).to_be_visible()
        expect(main.get_by_text("Leave Types", exact=True)).to_be_visible()
        expect(main.get_by_text("Work Modes", exact=True)).to_be_visible()

        browser.close()
