from playwright.sync_api import sync_playwright, expect
from utils.onboarding_helper import open_browser, open_review, review_row, SUBMITTED_CANDIDATE_ID


def test_contact_fields_no_reject():
    """RP-019: the mobile number and personal email (HR-entered contact details) can be approved or edited,
    but not sent back to the candidate, while other fields can."""
    with sync_playwright() as p:
        browser, page = open_browser(p)
        open_review(page, SUBMITTED_CANDIDATE_ID)

        for field in ["Personal Mobile Number", "Personal Email"]:
            row = review_row(page, field)
            expect(row.get_by_title("Approve")).to_be_visible()
            expect(row.get_by_title("Edit Value")).to_be_visible()
            expect(row.get_by_title("Reject")).to_have_count(0)
        expect(review_row(page, "Designation").get_by_title("Reject")).to_be_visible()

        browser.close()
