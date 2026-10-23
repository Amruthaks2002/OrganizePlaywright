from playwright.sync_api import sync_playwright, expect
from utils.onboarding_helper import (
    open_browser, open_review, review_row, set_field_mandatory, mandatory_fields, restore_mandatory_fields,
    SUBMITTED_CANDIDATE_ID,
)

FIELD = "Marital Status"  # FC-005 toggles Blood Group, keep them apart when run in parallel


def test_optional_field_on_review():
    """FC-007: the review page marks mandatory fields with * and drops it once the field is made optional."""
    with sync_playwright() as p:
        browser, page = open_browser(p)
        snapshot = mandatory_fields(page)
        try:
            open_review(page, SUBMITTED_CANDIDATE_ID)
            label = review_row(page, FIELD).locator("p").first
            expect(label).to_contain_text("*")

            set_field_mandatory(page, FIELD, False)
            open_review(page, SUBMITTED_CANDIDATE_ID)
            expect(label).to_have_text(FIELD, ignore_case=True)
        finally:
            restore_mandatory_fields(page, snapshot)

        browser.close()
