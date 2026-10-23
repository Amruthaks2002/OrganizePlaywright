from playwright.sync_api import sync_playwright, expect
from utils.people_portal_helper import (
    open_browser, open_browser_as, unique_prefix, create_queries, delete_queries, open_portal, query_rows,
    query_row, row_assignee, row_id, bulk_post, BULK_ASSIGN, BULK_DELETE, FASNA_ID,
)


def test_employee_cannot_touch_other_types():
    """PB-018: a query manager may only act on the categories assigned to their team. Ajith PT's
    "ID card query team" has the manage People Portal permission, but Manage -> People Portal Types
    gives it only ID/Biometric - so "Other queries" raised by someone else (HR here) stay hidden
    from him, and his bulk assign / delete calls on them change nothing.

    The queries must not be Ajith's own: owners may delete their own queries whatever the category."""
    with sync_playwright() as p:
        browser, page = open_browser(p)
        prefix = unique_prefix()
        try:
            subjects = create_queries(p, prefix, role="hr")
            open_portal(page, search=prefix)
            ids = [row_id(query_row(page, s)) for s in subjects]

            emp_browser, emp_page = open_browser_as(p, "employee")
            open_portal(emp_page, search=prefix)
            expect(query_rows(emp_page).filter(has_text=prefix)).to_have_count(0)
            bulk_post(emp_page, BULK_ASSIGN, {"query_ids": ids, "user_ids": [str(FASNA_ID)]})
            bulk_post(emp_page, BULK_DELETE, {"query_ids": ids})
            emp_browser.close()

            open_portal(page, search=prefix)
            expect(query_rows(page)).to_have_count(2)
            for subject in subjects:
                expect(row_assignee(query_row(page, subject))).to_have_text("Unassigned")
        finally:
            delete_queries(page, prefix)

        browser.close()
