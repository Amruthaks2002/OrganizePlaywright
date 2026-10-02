from playwright.sync_api import sync_playwright, expect
from utils.onboarding_helper import (
    open_browser, create_candidate, new_candidate_data, open_review, review_row, edit_field_value,
    delete_candidates,
)


def test_edit_value_invalid_email():
    """RP-018: saving a badly formatted personal email shows a format error and keeps the old email."""
    with sync_playwright() as p:
        browser, page = open_browser(p)
        data = new_candidate_data()
        try:
            candidate_id = create_candidate(page, **data)
            open_review(page, candidate_id)
            edit_field_value(page, "Personal Email", "not-an-email")
            expect(review_row(page, "Personal Email")).to_contain_text(
                "The personal email field must be a valid email address.")

            open_review(page, candidate_id)
            expect(review_row(page, "Personal Email")).to_contain_text(data["email"])
        finally:
            delete_candidates(page, data["name"])

        browser.close()
