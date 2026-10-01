import re
from playwright.sync_api import sync_playwright, expect
from utils.forms_helper import (
    open_browser, open_probation_reviews, unique_form_title, create_form_api, delete_forms, goto, main_content,
    BASE_URL,
)


def test_back_to_forms():
    """PR-007: ← Back to Forms returns to the probation forms list."""
    with sync_playwright() as p:
        browser, page = open_browser(p)
        open_probation_reviews(page)
        title = unique_form_title()
        try:
            form = create_form_api(page, title, type="probation_review")
            goto(page, f"{BASE_URL}/probation-reviews/form/{form['id']}")

            main_content(page).get_by_role("link", name="← Back to Forms").click()
            expect(page).to_have_url(re.compile(r"/probation-reviews$"))
            expect(main_content(page).get_by_role("heading", name="Probation Review Forms")).to_be_visible()
        finally:
            delete_forms(page, title)

        browser.close()
