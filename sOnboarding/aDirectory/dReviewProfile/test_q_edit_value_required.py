from playwright.sync_api import sync_playwright, expect
from utils.onboarding_helper import (
    open_browser, create_candidate, new_candidate_data, open_review, review_row, edit_field_value,
    delete_candidates,
)


def test_edit_value_required():
    """RP-017: clearing a mandatory field and saving shows a required error and keeps the old value."""
    with sync_playwright() as p:
        browser, page = open_browser(p)
        data = new_candidate_data()
        try:
            candidate_id = create_candidate(page, **data)
            open_review(page, candidate_id)
            edit_field_value(page, "Employee Name", "")
            expect(review_row(page, "Employee Name")).to_contain_text("The full name field is required.")

            open_review(page, candidate_id)
            expect(review_row(page, "Employee Name")).to_contain_text(data["name"])
        finally:
            delete_candidates(page, data["name"])

        browser.close()
