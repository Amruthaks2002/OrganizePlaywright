from playwright.sync_api import sync_playwright, expect
from utils.work_summary_helper import open_browser, log_hours, open_edit, edit_dialog, expect_toast, UPDATED, ADMIN_NAME
from utils.work_summary_bulk_helper import (bulk_prefix, entry_desc, create_logs, show_entries, earliest, tick, expect_dock,
                                            dock, find_prefixed, CREATED_LOG_IDS, cleanup_prefixed)


def test_log_and_edit_clear():
    """WS-063: logging new hours and saving an edit both refetch the table, which drops the selection."""
    with sync_playwright() as p:
        browser, page = open_browser(p)
        prefix = bulk_prefix()
        try:
            [log] = create_logs(page, prefix, 1)
            day = earliest([log])
            show_entries(page, "Comp Hours", day, employee=ADMIN_NAME)

            tick(page, log["description"])
            expect_dock(page, 1)
            log_hours(page, entry_desc(prefix, 2), hours=1, work_date=day)
            CREATED_LOG_IDS.update(l["id"] for l in find_prefixed(page, prefix))
            expect(dock(page)).to_have_count(0)

            tick(page, log["description"])
            expect_dock(page, 1)
            dialog = open_edit(page, log["description"])
            dialog.locator("input[type=number]").fill("2")
            dialog.get_by_role("button", name="Update").click()
            expect_toast(page, UPDATED)
            expect(edit_dialog(page)).to_have_count(0)
            expect(dock(page)).to_have_count(0)
        finally:
            cleanup_prefixed(page, prefix)
            browser.close()
