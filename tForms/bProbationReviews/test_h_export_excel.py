import re
from playwright.sync_api import sync_playwright
from utils.forms_helper import (
    open_browser, open_probation_reviews, unique_form_title, create_form_api, delete_forms, goto, main_content,
    BASE_URL,
)


def test_export_excel():
    """PR-008: Export Excel downloads the probation reviews as an .xlsx file."""
    with sync_playwright() as p:
        browser, page = open_browser(p)
        open_probation_reviews(page)
        title = unique_form_title()
        try:
            form = create_form_api(page, title, type="probation_review")
            goto(page, f"{BASE_URL}/probation-reviews/form/{form['id']}")

            with page.expect_download() as download:
                main_content(page).get_by_role("button", name="Export Excel").click()
            assert re.fullmatch(r"probation_reviews_[\d_]+\.xlsx", download.value.suggested_filename), \
                download.value.suggested_filename
        finally:
            delete_forms(page, title)

        browser.close()
