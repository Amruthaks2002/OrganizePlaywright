from playwright.sync_api import sync_playwright, expect
from utils.app_usage_helper import (open_browser, open_app_usage, main_content, install_rows, installs_count,
                                    filter_installs, installs_status_select, query_params, STATUSES, INSTALLS_EMPTY)


def test_status_filter():
    """AI-008: each version-status option lists only installs with that status (or the empty message)."""
    with sync_playwright() as p:
        browser, page = open_browser(p)
        open_app_usage(page)
        total = installs_count(page)
        options = installs_status_select(page).locator("option").all_inner_texts()
        assert [o.strip() for o in options] == ["Any version"] + list(STATUSES.values()), options

        counts = 0
        for value, label in STATUSES.items():
            filter_installs(page, status=value)
            assert query_params(page).get("status") == value, page.url
            rows = install_rows(page)
            assert all(r["status"] == label for r in rows), (label, rows)
            assert installs_count(page) == len(rows)
            if not rows:
                expect(main_content(page).get_by_text(INSTALLS_EMPTY)).to_be_visible()
            counts += len(rows)
        assert counts == total, (counts, total)

        browser.close()
