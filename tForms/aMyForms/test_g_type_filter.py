import re
from playwright.sync_api import sync_playwright, expect
from utils.forms_helper import (
    open_browser, open_my_forms, unique_form_title, create_form_api, delete_forms, search_forms, type_filter,
    row_titles, settle,
)


def test_type_filter():
    """FM-007: the type filter shows only General, only Probation Review, or all forms."""
    with sync_playwright() as p:
        browser, page = open_browser(p)
        open_my_forms(page)
        base = unique_form_title()
        try:
            create_form_api(page, f"{base} General")
            create_form_api(page, f"{base} Probation", type="probation_review")
            search_forms(page, base)

            type_filter(page).select_option("general")
            expect(page).to_have_url(re.compile("type=general"))
            settle(page)
            assert row_titles(page) == [f"{base} General"]

            type_filter(page).select_option("probation_review")
            expect(page).to_have_url(re.compile("type=probation_review"))
            settle(page)
            assert row_titles(page) == [f"{base} Probation"]

            type_filter(page).select_option("")
            expect(page).to_have_url(re.compile("type=(&|$)"))
            settle(page)
            assert sorted(row_titles(page)) == [f"{base} General", f"{base} Probation"]
        finally:
            delete_forms(page, base)

        browser.close()
