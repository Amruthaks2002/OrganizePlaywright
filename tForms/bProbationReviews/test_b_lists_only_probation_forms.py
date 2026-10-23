from playwright.sync_api import sync_playwright, expect
from utils.forms_helper import (
    open_browser, open_probation_reviews, unique_form_title, create_form_api, delete_forms, search_forms,
    form_row, row_titles,
)


def test_lists_only_probation_forms():
    """PR-002: only Probation Review forms are listed, each with a Probation badge."""
    with sync_playwright() as p:
        browser, page = open_browser(p)
        open_probation_reviews(page)
        base = unique_form_title()
        try:
            create_form_api(page, f"{base} General")
            create_form_api(page, f"{base} Probation", type="probation_review")
            search_forms(page, base)

            assert row_titles(page) == [f"{base} Probation"]
            expect(form_row(page, f"{base} Probation").get_by_text("Probation", exact=True)).to_be_visible()
        finally:
            delete_forms(page, base)

        browser.close()
