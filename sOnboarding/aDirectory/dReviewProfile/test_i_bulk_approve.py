from playwright.sync_api import sync_playwright, expect
from utils.onboarding_helper import (
    open_browser, create_candidate, new_candidate_data, open_review, review_row, row_status, review_counters,
    section_approve_selected, approve_selected, delete_candidates, NEW_CANDIDATE_PENDING,
)

FIELDS = ["Blood Group", "Marital Status"]


def test_bulk_approve():
    """RP-009: ticking two fields and confirming Approve Selected approves both."""
    with sync_playwright() as p:
        browser, page = open_browser(p)
        data = new_candidate_data()
        try:
            candidate_id = create_candidate(page, **data)
            open_review(page, candidate_id)
            for field in FIELDS:
                review_row(page, field).locator("input[type=checkbox]").check()
            approve_selected(page, section_approve_selected(page))

            open_review(page, candidate_id)
            for field in FIELDS:
                expect(row_status(review_row(page, field))).to_have_text("approved", ignore_case=True)
            assert review_counters(page) == (2, 0, NEW_CANDIDATE_PENDING - 2), review_counters(page)
        finally:
            delete_candidates(page, data["name"])

        browser.close()
