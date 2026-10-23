from datetime import timedelta
from playwright.sync_api import sync_playwright, expect
from utils.work_summary_helper import (open_browser, open_hours, open_tab, from_date, to_date, wait_for_logs, log_hours,
                                       data_rows, unique_desc, cleanup_logs, today, main_content, EMPTY_TITLE)


def test_from_after_to():
    """WS-026: a From date after the To date matches nothing - the table shows its empty state, not
    today's logs or an error."""
    with sync_playwright() as p:
        browser, page = open_browser(p)
        desc = unique_desc("range")
        try:
            open_hours(page)
            log_hours(page, desc)
            open_tab(page, "Regular Hours")

            wait_for_logs(page, lambda: to_date(page).fill((today() - timedelta(days=1)).isoformat()))
            data = wait_for_logs(page, lambda: from_date(page).fill(today().isoformat()))
            assert data["timeLogs"]["total"] == 0, data["timeLogs"]["total"]
            assert data_rows(page) == []
            expect(main_content(page).get_by_text(EMPTY_TITLE)).to_be_visible()
        finally:
            cleanup_logs(page, desc)
            browser.close()
