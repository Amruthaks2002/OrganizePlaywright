from playwright.sync_api import sync_playwright, expect
from utils.onboarding_helper import open_browser, open_review, review_row, reject_dialog, SUBMITTED_CANDIDATE_ID


def test_reject_dialog():
    """RP-010: Reject opens a dialog naming the field, with a Correction Note box, Cancel and Submit Rejection."""
    with sync_playwright() as p:
        browser, page = open_browser(p)
        open_review(page, SUBMITTED_CANDIDATE_ID)

        review_row(page, "Designation").get_by_title("Reject").click()
        dialog = reject_dialog(page)
        expect(dialog).to_be_visible()
        expect(dialog.get_by_text("Designation", exact=True)).to_be_visible()
        expect(dialog.get_by_text("Correction Note", exact=False)).to_be_visible()
        expect(dialog.get_by_placeholder("Tell the candidate what needs fixing...")).to_have_value("")
        expect(dialog.get_by_role("button", name="Cancel")).to_be_visible()
        expect(dialog.get_by_role("button", name="SUBMIT REJECTION")).to_be_visible()

        dialog.get_by_role("button", name="Cancel").click()

        browser.close()
