from playwright.sync_api import sync_playwright
from utils.leave_policy_helper import (
    open_browser, open_leave_policies, existing_policy_names, is_test_policy, open_create_form, copy_source,
)


def test_copy_source_lists_all_policies():
    """LP-025: both copy-source dropdowns list every existing policy."""
    with sync_playwright() as p:
        browser, page = open_browser(p)
        open_leave_policies(page)
        names = existing_policy_names(page)

        form = open_create_form(page)
        for column in ["Copy Leave Type", "Copy Work Mode"]:
            options = copy_source(form, column).evaluate("e => [...e.options].map(o => o.text.trim())")
            options = [o for o in options if not is_test_policy(o)]
            assert sorted(options) == sorted(names), column

        browser.close()
