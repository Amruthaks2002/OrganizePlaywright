import re
from playwright.sync_api import sync_playwright, expect
from utils.forms_helper import (
    open_browser, open_my_forms, unique_form_title, create_form_api, toggle_status_api, delete_forms,
    search_forms, status_filter, row_titles, settle,
)


def test_status_filter():
    """FM-006: the status filter shows only Active, only Inactive, or all forms."""
    with sync_playwright() as p:
        browser, page = open_browser(p)
        open_my_forms(page)
        base = unique_form_title()
        try:
            create_form_api(page, f"{base} On")
            off = create_form_api(page, f"{base} Off")
            toggle_status_api(page, off["id"])
            search_forms(page, base)

            status_filter(page).select_option("active")
            expect(page).to_have_url(re.compile("status=active"))
            settle(page)
            assert row_titles(page) == [f"{base} On"]

            status_filter(page).select_option("inactive")
            expect(page).to_have_url(re.compile("status=inactive"))
            settle(page)
            assert row_titles(page) == [f"{base} Off"]

            status_filter(page).select_option("")
            expect(page).to_have_url(re.compile("status=(&|$)"))
            settle(page)
            assert sorted(row_titles(page)) == [f"{base} Off", f"{base} On"]
        finally:
            delete_forms(page, base)

        browser.close()
