import pytest
from playwright.sync_api import sync_playwright, expect
from utils.work_summary_helper import open_browser, expect_toast, data_rows, row_cells, PER_PAGE, ADMIN_NAME
from utils.work_summary_bulk_helper import (bulk_prefix, create_logs, show_entries, earliest, latest, header_checkbox,
                                            run_bulk, expect_dock, find_prefixed, deleted_msg, cleanup_prefixed, me)


def test_select_all_full_page():
    """WS-073: with 16 of the admin's regular logs in range, 'select all' ticks the 15 on page 1 and deletes
    exactly those; the 16th moves up to page 1. Before deleting, checks every ticked row is this test's own."""
    with sync_playwright() as p:
        browser, page = open_browser(p)
        prefix = bulk_prefix()
        try:
            logs = create_logs(page, prefix, PER_PAGE + 1, comp=False)
            data = show_entries(page, "Regular Hours", earliest(logs), end=latest(logs), employee=ADMIN_NAME)
            if data["timeLogs"]["total"] != PER_PAGE + 1:
                others = [l for l in find_prefixed(page, "", employee_id=me(page)["id"])
                          if not (l["description"] or "").startswith(prefix)
                          and earliest(logs) <= earliest([l]) <= latest(logs) and not l["is_weekend_or_holiday"]]
                pytest.fail(f"other regular logs of {ADMIN_NAME} in range: "
                            f"{[(l['id'], l['work_date'][:10], l['description']) for l in others]}")
            assert all(row_cells(tr)[-1].startswith(prefix) for tr in data_rows(page))

            header_checkbox(page).check()
            expect_dock(page, PER_PAGE, delete=PER_PAGE)
            sent = run_bulk(page, "Delete")
            assert len(sent) == PER_PAGE and set(sent) <= {log["id"] for log in logs}, sent

            expect_toast(page, deleted_msg(PER_PAGE))
            [left] = find_prefixed(page, prefix)
            assert left["id"] not in sent
            expect(page.get_by_text(left["description"], exact=True)).to_be_visible()
            assert len(data_rows(page)) == 1
        finally:
            cleanup_prefixed(page, prefix)
            browser.close()
