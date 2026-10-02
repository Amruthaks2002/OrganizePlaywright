from playwright.sync_api import sync_playwright, expect
from utils.onboarding_helper import (
    open_browser, create_candidate, new_candidate_data, open_review, review_row, save_field_value,
    delete_candidates,
)


def test_edit_value():
    """RP-016: saving an edited value updates the field."""
    with sync_playwright() as p:
        browser, page = open_browser(p)
        data = new_candidate_data()
        try:
            candidate_id = create_candidate(page, **data)
            open_review(page, candidate_id)
            save_field_value(page, "Designation", "QA Engineer")

            open_review(page, candidate_id)
            expect(review_row(page, "Designation")).to_contain_text("QA Engineer")
        finally:
            delete_candidates(page, data["name"])

        browser.close()
