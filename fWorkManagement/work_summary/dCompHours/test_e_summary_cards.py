from playwright.sync_api import sync_playwright, expect
from utils.work_summary_helper import (open_browser, open_hours, open_tab, pick_employee, wait_for_logs, summary_card,
                                       card_number, main_content, EMPLOYEE_NAME)

CARDS = ["Pending Comp Hours", "Convertible Balance", "Approved Comp Hours", "Leave Balance"]


def test_summary_cards():
    """WS-034: the comp summary cards only appear once an employee is picked, and show that employee's
    totals from the server."""
    with sync_playwright() as p:
        browser, page = open_browser(p)
        open_hours(page)
        open_tab(page, "Comp Hours")
        for title in CARDS:
            expect(main_content(page).get_by_text(title, exact=True)).to_have_count(0)

        data = wait_for_logs(page, lambda: pick_employee(page, EMPLOYEE_NAME))
        for title in CARDS:
            expect(summary_card(page, title)).to_be_visible()

        pending, balance = summary_card(page, "Pending Comp Hours"), summary_card(page, "Convertible Balance")
        approved, leave = summary_card(page, "Approved Comp Hours"), summary_card(page, "Leave Balance")
        assert card_number(pending, "Total Hours") == data["totalPendingCompensatoryHours"], data
        assert card_number(pending, "Convertible Days") == data["totalPendingCompLeaveDays"], data
        assert card_number(balance) == data["remainingCompOffHours"], data
        assert card_number(approved, "Total Hours") == data["totalApprovedCompensatoryHours"], data
        assert card_number(approved, "Converted Days") == data["totalApprovedCompLeaveDays"], data
        assert card_number(leave) == data["compOffBalance"], data
        expect(balance).to_contain_text("Available for conversion")
        expect(leave).to_contain_text("Available leaves")

        browser.close()
