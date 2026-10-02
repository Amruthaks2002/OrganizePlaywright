import re
from playwright.sync_api import sync_playwright, expect
from utils.onboarding_helper import open_browser, open_review, open_section, current_section, review_row, SUBMITTED_CANDIDATE_ID


def test_section_navigation():
    """RP-002: picking a section in the navigation shows that section's fields."""
    with sync_playwright() as p:
        browser, page = open_browser(p)
        open_review(page, SUBMITTED_CANDIDATE_ID)
        expect(review_row(page, "Designation")).to_be_visible()

        open_section(page, "Academic Certificates")
        for field in ["Class 10 Certificate", "Class 12 Certificate", "Graduation Certificate"]:
            expect(review_row(page, field)).to_be_visible()
        expect(review_row(page, "Designation")).to_have_count(0)

        open_section(page, "Basic Information")
        expect(current_section(page).locator("h3")).to_have_text(re.compile("Basic Information", re.I))
        expect(review_row(page, "Designation")).to_be_visible()

        browser.close()
