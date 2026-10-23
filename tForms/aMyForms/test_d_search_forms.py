from playwright.sync_api import sync_playwright
from utils.forms_helper import (
    open_browser, open_my_forms, unique_form_title, create_form_api, delete_forms, search_forms, row_titles,
)


def test_search_forms():
    """FM-004: searching by title only lists the matching forms."""
    with sync_playwright() as p:
        browser, page = open_browser(p)
        open_my_forms(page)
        base = unique_form_title()
        try:
            create_form_api(page, f"{base} Alpha")
            create_form_api(page, f"{base} Beta")

            search_forms(page, base)
            assert sorted(row_titles(page)) == [f"{base} Alpha", f"{base} Beta"]

            search_forms(page, f"{base} Alpha")
            assert row_titles(page) == [f"{base} Alpha"]
        finally:
            delete_forms(page, base)

        browser.close()
