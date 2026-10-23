from playwright.sync_api import sync_playwright
from utils.work_summary_helper import open_browser, open_browser_as, data_rows, row_cells
from utils.work_summary_bulk_helper import (bulk_prefix, create_logs, show_entries, earliest, header_checkbox, expect_dock, me,
                                            cleanup_prefixed)


def test_employee_select_all_own_rows():
    """WS-099: an employee's Comp Hours only lists their own entries, so 'select all' only ticks theirs: Delete
    counts their pending ones, and Approve (0) / Reject (0) stay disabled."""
    with sync_playwright() as p:
        admin_browser, admin = open_browser(p)
        browser, page = open_browser_as(p, "employee")
        prefix = bulk_prefix()
        try:
            logs = create_logs(page, prefix, 2)
            name = me(page)["name"]
            data = show_entries(page, "Comp Hours", earliest(logs))
            listed = data["timeLogs"]["data"]
            assert {row_cells(tr)[1] for tr in data_rows(page)} == {name}
            deletable = [l for l in listed if l["can"]["delete"] and l["comp_off_status"] == "pending"]

            header_checkbox(page).check()
            expect_dock(page, len(listed), approve=0, reject=0, delete=len(deletable))
        finally:
            cleanup_prefixed(admin, prefix)
            browser.close()
            admin_browser.close()
