from playwright.sync_api import sync_playwright, expect
from utils.work_summary_helper import (open_browser, open_hours, pick_employee, wait_for_chart, main_content,
                                       ADMIN_NAME, EMPLOYEE_NAME)


def test_weekly_hours_heading_names_user():
    """WS-039: the single-user chart is titled with whose hours it shows - 'Weekly Hours — <name>' - both for
    My Hours and for an employee picked in the search.

    Known bug: the heading ends at the dash ('Weekly Hours —') with no name after it. This test fails until
    that's fixed."""
    with sync_playwright() as p:
        browser, page = open_browser(p)
        open_hours(page)
        title = main_content(page).locator("h3").first

        main_content(page).get_by_role("button", name="My Hours", exact=True).click()
        expect(title).to_have_text(f"Weekly Hours — {ADMIN_NAME}")

        wait_for_chart(page, lambda: pick_employee(page, EMPLOYEE_NAME))
        expect(title).to_have_text(f"Weekly Hours — {EMPLOYEE_NAME}")

        browser.close()
