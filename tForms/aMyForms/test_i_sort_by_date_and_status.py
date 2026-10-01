import re
from playwright.sync_api import sync_playwright, expect
from utils.forms_helper import (
    open_browser, open_my_forms, unique_form_title, create_form_api, toggle_status_api, delete_forms,
    search_forms, sort_header, row_titles, settle,
)


def test_sort_by_date_and_status():
    """FM-009: Created Date and Status column headers sort the list both ways."""
    with sync_playwright() as p:
        browser, page = open_browser(p)
        open_my_forms(page)
        base = unique_form_title()
        older, newer = f"{base} Older", f"{base} Newer"
        try:
            create_form_api(page, older)
            create_form_api(page, newer)
            toggle_status_api(page, create_form_api(page, f"{base} Inactive")["id"])
            search_forms(page, base)

            # newest first by default
            assert row_titles(page)[:2] == [f"{base} Inactive", newer]

            sort_header(page, "Created Date").click()
            expect(page).to_have_url(re.compile("sort=created_at"))
            expect(page).to_have_url(re.compile("direction=asc"))
            settle(page)
            assert row_titles(page) == [older, newer, f"{base} Inactive"]

            sort_header(page, "Status").click()
            expect(page).to_have_url(re.compile("sort=status"))
            settle(page)
            first = row_titles(page)
            sort_header(page, "Status").click()
            expect(page).to_have_url(re.compile("direction=desc"))
            settle(page)
            second = row_titles(page)
            # the inactive form sits at one end of the list, and moves to the other end
            assert f"{base} Inactive" in (first[0], first[-1]), first
            assert first.index(f"{base} Inactive") != second.index(f"{base} Inactive"), (first, second)
        finally:
            delete_forms(page, base)

        browser.close()
