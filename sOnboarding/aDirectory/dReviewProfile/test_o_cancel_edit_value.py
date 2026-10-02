from playwright.sync_api import sync_playwright, expect
from utils.onboarding_helper import open_browser, open_review, review_row, SUBMITTED_CANDIDATE_ID


def test_cancel_edit_value():
    """RP-015: Cancel discards the edit and shows the original value."""
    with sync_playwright() as p:
        browser, page = open_browser(p)
        open_review(page, SUBMITTED_CANDIDATE_ID)
        row = review_row(page, "Designation")

        row.get_by_title("Edit Value").click()
        row.locator("input[type=text]").fill("should not be saved")
        row.get_by_role("button", name="Cancel", exact=True).click()
        expect(row.locator("input[type=text]")).to_have_count(0)
        expect(row).to_contain_text("hfghfg")

        open_review(page, SUBMITTED_CANDIDATE_ID)
        expect(review_row(page, "Designation")).to_contain_text("hfghfg")
        expect(review_row(page, "Designation")).not_to_contain_text("should not be saved")

        browser.close()
