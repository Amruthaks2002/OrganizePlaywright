from playwright.sync_api import sync_playwright, expect
from utils.leave_policy_helper import (
    open_browser, open_leave_policies, policy_names, select_policy, items_count, item_rows,
)


def test_leave_types_and_work_modes():
    """LP-006: Leave Types and Work Modes list each item with its code, and the counts match the rows."""
    with sync_playwright() as p:
        browser, page = open_browser(p)
        open_leave_policies(page)

        for name in policy_names(page):
            select_policy(page, name)
            for section in ["Leave Types", "Work Modes"]:
                rows = item_rows(page, section)
                assert items_count(page, section) == rows.count(), f"{name} / {section}"
                for row in rows.all():
                    expect(row.locator("span").first).not_to_be_empty()
                    expect(row.locator("span").last).not_to_be_empty()

        browser.close()
