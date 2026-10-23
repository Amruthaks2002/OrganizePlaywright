from playwright.sync_api import sync_playwright, expect
from utils.onboarding_helper import (
    open_browser, create_candidate, new_candidate_data, open_review, review_row, row_status, reject_dialog,
    delete_candidates,
)


def test_reject_without_note():
    """RP-013: Submit Rejection with an empty correction note is blocked (the candidate needs to know what to fix).

    Known bug: the rejection goes through with no note at all. This test fails until that's fixed.
    """
    with sync_playwright() as p:
        browser, page = open_browser(p)
        data = new_candidate_data()
        try:
            candidate_id = create_candidate(page, **data)
            open_review(page, candidate_id)
            review_row(page, "Gender").get_by_title("Reject").click()
            dialog = reject_dialog(page)
            dialog.get_by_role("button", name="SUBMIT REJECTION").click()
            page.wait_for_timeout(2000)

            open_review(page, candidate_id)
            expect(row_status(review_row(page, "Gender")), "rejected without a note").to_have_text(
                "pending", ignore_case=True)
        finally:
            delete_candidates(page, data["name"])

        browser.close()
