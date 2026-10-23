from playwright.sync_api import sync_playwright, expect
from utils.work_summary_helper import (open_browser_as, open_hours, open_tab, page_props, main_content, employee_search,
                                       team_select, export_button, data_rows, row_cells, approve_button, reject_button,
                                       summary_card, EMPLOYEE_NAME)


def test_employee_view():
    """WS-040: an employee gets the personal version of the page - only their own logs, no employee/team
    filters, no Team/My Hours switch, no Export and no Approve/Reject - plus their comp summary cards."""
    with sync_playwright() as p:
        browser, page = open_browser_as(p, "employee")
        open_hours(page)
        main = main_content(page)
        props = page_props(page)
        assert props["canViewAll"] is False and props["canApprove"] is False, props

        expect(main).to_contain_text("Log hours and track compensation.")
        expect(main.get_by_role("heading", name="My Work Hours")).to_be_visible()
        expect(main.get_by_role("button", name="Log Hours")).to_be_visible()
        expect(employee_search(page)).to_have_count(0)
        expect(main.get_by_text("Team", exact=True)).to_have_count(0)
        expect(main.get_by_role("button", name="Team Hours")).to_have_count(0)
        expect(main.get_by_role("button", name="My Hours")).to_have_count(0)

        open_tab(page, "Regular Hours")
        assert {row_cells(tr)[0] for tr in data_rows(page)} <= {EMPLOYEE_NAME}
        expect(main.locator("select")).to_have_count(0)

        open_tab(page, "Comp Hours")
        assert {row_cells(tr)[0] for tr in data_rows(page)} <= {EMPLOYEE_NAME}
        expect(main.locator("select")).to_have_count(1)  # just Status
        expect(export_button(page)).to_have_count(0)
        for tr in data_rows(page):
            expect(approve_button(tr)).to_have_count(0)
            expect(reject_button(tr)).to_have_count(0)
        for title in ["Pending Comp Hours", "Convertible Balance", "Approved Comp Hours", "Leave Balance"]:
            expect(summary_card(page, title)).to_be_visible()

        browser.close()
