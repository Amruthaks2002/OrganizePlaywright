from playwright.sync_api import sync_playwright, expect
from utils.work_summary_helper import open_browser, data_rows, rows, last_weekend_day, EMPTY_TITLE, ADMIN_NAME
from utils.work_summary_bulk_helper import show_entries, header_checkbox, dock


def test_empty_table_select_all_disabled():
    """WS-057: with no rows (Regular Hours on a weekend day - weekend hours always go to Comp Hours) the
    header checkbox is disabled and there is no dock."""
    with sync_playwright() as p:
        browser, page = open_browser(p)
        day = last_weekend_day()
        data = show_entries(page, "Regular Hours", day, end=day, employee=ADMIN_NAME)
        assert data["timeLogs"]["total"] == 0, data["timeLogs"]
        expect(rows(page).filter(has_text=EMPTY_TITLE)).to_have_count(1)
        assert not data_rows(page)
        expect(header_checkbox(page)).to_be_disabled()
        expect(header_checkbox(page)).not_to_be_checked()
        expect(dock(page)).to_have_count(0)
        browser.close()
