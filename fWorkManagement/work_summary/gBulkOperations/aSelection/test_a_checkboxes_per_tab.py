from playwright.sync_api import sync_playwright, expect
from utils.work_summary_helper import open_browser, open_hours, open_tab, main_content, data_rows, ADMIN_NAME
from utils.work_summary_bulk_helper import (bulk_prefix, create_logs, show_entries, earliest, header_checkbox, row_checkbox,
                                            dock, cleanup_prefixed)


def test_checkboxes_per_tab():
    """WS-051: Chart View has no checkboxes and no selection dock; Regular Hours and Comp Hours have a 'select
    all' checkbox in the header and one checkbox per row, all unticked to start with."""
    with sync_playwright() as p:
        browser, page = open_browser(p)
        prefix = bulk_prefix()
        try:
            comp = create_logs(page, prefix, 1)
            regular = create_logs(page, prefix, 1, comp=False, start_index=2)

            open_hours(page)
            expect(main_content(page).locator("input[type=checkbox]")).to_have_count(0)
            expect(dock(page)).to_have_count(0)

            for tab, logs in [("Regular Hours", regular), ("Comp Hours", comp)]:
                show_entries(page, tab, earliest(logs), employee=ADMIN_NAME)
                trs = data_rows(page)
                assert trs, f"{tab}: no rows"
                expect(header_checkbox(page)).to_be_enabled()
                expect(header_checkbox(page)).not_to_be_checked()
                for tr in trs:
                    expect(row_checkbox(tr)).to_have_count(1)
                    expect(row_checkbox(tr)).not_to_be_checked()
                    expect(row_checkbox(tr)).to_have_attribute("aria-label", f"Select {ADMIN_NAME}")
                expect(main_content(page).locator("table input[type=checkbox]")).to_have_count(len(trs) + 1)
                expect(dock(page)).to_have_count(0)
        finally:
            cleanup_prefixed(page, prefix)
            browser.close()
