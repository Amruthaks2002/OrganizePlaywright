from playwright.sync_api import sync_playwright, expect
from utils.onboarding_helper import open_browser, open_directory, candidate_row, review_url, main_content, SUBMITTED_CANDIDATE_ID


def test_review_profile_link():
    """OD-017: Review Profile opens the candidate's onboarding review."""
    with sync_playwright() as p:
        browser, page = open_browser(p)
        open_directory(page, search="maju")

        candidate_row(page, "maju").get_by_role("link", name="Review Profile").click()
        expect(page).to_have_url(review_url(SUBMITTED_CANDIDATE_ID))
        expect(main_content(page).get_by_role("heading", name="maju")).to_be_visible()

        browser.close()
