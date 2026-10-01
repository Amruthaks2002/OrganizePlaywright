from playwright.sync_api import sync_playwright
from utils.leave_policy_helper import (
    open_browser, open_leave_policies, unique_policy_name, create_policy, delete_policy, select_policy,
    items_count, item_rows,
)


def test_create_without_copying():
    """LP-031: a policy created without copying has no leave types or work modes."""
    with sync_playwright() as p:
        browser, page = open_browser(p)
        open_leave_policies(page)
        name = unique_policy_name()
        try:
            create_policy(page, name)

            select_policy(page, name)
            for section in ["Leave Types", "Work Modes"]:
                assert items_count(page, section) == 0, section
                assert item_rows(page, section).count() == 0, section
        finally:
            delete_policy(page, name)

        browser.close()
