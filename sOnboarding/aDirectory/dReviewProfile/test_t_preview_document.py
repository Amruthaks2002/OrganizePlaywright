from playwright.sync_api import sync_playwright, expect
from utils.onboarding_helper import (
    open_browser, open_review, open_section, review_row, cross_check_panel, SUBMITTED_CANDIDATE_ID,
)


def test_preview_document():
    """RP-020: Preview File opens the uploaded document in the Cross Check panel, which can be closed."""
    with sync_playwright() as p:
        browser, page = open_browser(p)
        open_review(page, SUBMITTED_CANDIDATE_ID)
        open_section(page, "Academic Certificates")

        review_row(page, "Class 10 Certificate").get_by_role("button", name="Preview File").click()
        panel = cross_check_panel(page)
        expect(panel).to_be_visible()
        expect(panel).to_contain_text("Class 10 Certificate")
        image = panel.locator("img").first
        expect(image).to_be_visible()
        assert image.evaluate("img => img.complete && img.naturalWidth > 0"), "the document image didn't load"

        panel.locator("button").first.click()
        expect(panel).to_have_count(0)

        browser.close()
