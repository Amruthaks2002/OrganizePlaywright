from playwright.sync_api import sync_playwright, expect
from utils.onboarding_helper import (
    open_browser, open_review, review_row, row_status, reject_dialog, review_counters, SUBMITTED_CANDIDATE_ID,
)


def test_cancel_reject():
    """RP-011: cancelling the Reject dialog leaves the field and counters unchanged."""
    with sync_playwright() as p:
        browser, page = open_browser(p)
        open_review(page, SUBMITTED_CANDIDATE_ID)
        counters = review_counters(page)

        review_row(page, "Designation").get_by_title("Reject").click()
        dialog = reject_dialog(page)
        dialog.locator("textarea").fill("should not be sent")
        dialog.get_by_role("button", name="Cancel").click()
        expect(dialog).to_be_hidden()

        open_review(page, SUBMITTED_CANDIDATE_ID)
        expect(row_status(review_row(page, "Designation"))).to_have_text("pending", ignore_case=True)
        assert review_counters(page) == counters, review_counters(page)

        browser.close()
