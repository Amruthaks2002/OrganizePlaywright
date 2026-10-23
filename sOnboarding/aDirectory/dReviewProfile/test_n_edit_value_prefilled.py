from playwright.sync_api import sync_playwright, expect
from utils.onboarding_helper import open_browser, open_review, review_row, SUBMITTED_CANDIDATE_ID


def test_edit_value_prefilled():
    """RP-014: Edit Value turns the field into an input holding the current value, with Save and Cancel."""
    with sync_playwright() as p:
        browser, page = open_browser(p)
        open_review(page, SUBMITTED_CANDIDATE_ID)
        row = review_row(page, "Designation")

        row.get_by_title("Edit Value").click()
        expect(row.locator("input[type=text]")).to_have_value("hfghfg")
        expect(row.get_by_role("button", name="Save", exact=True)).to_be_visible()
        expect(row.get_by_role("button", name="Cancel", exact=True)).to_be_visible()

        row.get_by_role("button", name="Cancel", exact=True).click()

        browser.close()
