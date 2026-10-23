from playwright.sync_api import sync_playwright
from utils.forms_helper import (
    open_browser, open_my_forms, unique_form_title, create_form_api, delete_forms, search_forms, sort_header,
    row_titles, settle,
)


def test_sort_by_title():
    """FM-010: clicking the Forms column header sorts the list by title."""
    with sync_playwright() as p:
        browser, page = open_browser(p)
        open_my_forms(page)
        base = unique_form_title()
        try:
            create_form_api(page, f"{base} Apple")
            create_form_api(page, f"{base} Banana")
            search_forms(page, base)
            # newest first by default
            assert row_titles(page) == [f"{base} Banana", f"{base} Apple"]

            sort_header(page, "Forms").click()
            page.wait_for_timeout(1500)
            settle(page)
            assert row_titles(page) == [f"{base} Apple", f"{base} Banana"], "clicking Forms did not sort by title"
        finally:
            delete_forms(page, base)

        browser.close()
