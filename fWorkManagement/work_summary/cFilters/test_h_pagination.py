from datetime import date
import pytest
from playwright.sync_api import sync_playwright, expect
from utils.work_summary_helper import (open_browser, open_hours, open_tab, from_date, wait_for_logs, data_rows, row_cells,
                                       footer_text, pager_button, today, PER_PAGE)


def test_pagination():
    """WS-028: the table shows 15 logs a page; Next / page numbers load the following page and Previous is
    disabled on page 1."""
    with sync_playwright() as p:
        browser, page = open_browser(p)
        open_hours(page)
        open_tab(page, "Comp Hours")
        data = wait_for_logs(page, lambda: from_date(page).fill(date(today().year, 1, 1).isoformat()))
        total = data["timeLogs"]["total"]
        if total <= PER_PAGE:
            pytest.skip(f"only {total} comp logs this year - need more than {PER_PAGE} for a second page")

        assert footer_text(page) == f"Showing 1 to {PER_PAGE} of {total} results"
        assert len(data_rows(page)) == PER_PAGE
        assert "cursor-not-allowed" in pager_button(page, "« Previous").get_attribute("class")
        first_page = [row_cells(tr) for tr in data_rows(page)]

        with page.expect_request(lambda r: "page=2" in r.url):
            page2 = wait_for_logs(page, lambda: pager_button(page, "Next »").click())
        assert page2["timeLogs"]["current_page"] == 2
        last = min(2 * PER_PAGE, total)
        assert footer_text(page) == f"Showing {PER_PAGE + 1} to {last} of {total} results"
        assert len(data_rows(page)) == last - PER_PAGE
        assert [row_cells(tr) for tr in data_rows(page)] != first_page
        assert "cursor-not-allowed" not in (pager_button(page, "« Previous").get_attribute("class") or "")

        wait_for_logs(page, lambda: pager_button(page, "1").click())
        assert footer_text(page) == f"Showing 1 to {PER_PAGE} of {total} results"
        assert [row_cells(tr) for tr in data_rows(page)] == first_page

        browser.close()
