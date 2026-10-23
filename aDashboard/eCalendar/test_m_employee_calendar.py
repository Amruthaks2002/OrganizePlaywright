from playwright.sync_api import sync_playwright
from utils.dashboard_helper import open_browser_as, chip_count, retry_if_data_changed

COMPANY_WIDE = ["HOLIDAYS", "BIRTHDAYS", "ANNIVERSARIES"]


def counts(page):
    return {label: chip_count(page, label) for label in COMPANY_WIDE}


def test_employee_calendar():
    """DB-037: an employee's calendar shows the same company-wide holidays, birthdays and anniversaries
    as the admin's.

    Leaves and work mode entries are per person (each user sees their own), so they are not compared."""
    with sync_playwright() as p:
        def check():
            browser, page = open_browser_as(p, "admin")
            admin = counts(page)
            browser.close()

            browser, page = open_browser_as(p, "employee")
            employee = counts(page)
            browser.close()

            for label in COMPANY_WIDE:
                assert employee[label] == admin[label], f"{label}: employee {employee[label]}, admin {admin[label]}"

        retry_if_data_changed(check)
