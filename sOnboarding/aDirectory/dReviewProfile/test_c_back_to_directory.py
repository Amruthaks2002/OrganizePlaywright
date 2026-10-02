from playwright.sync_api import sync_playwright, expect
from utils.onboarding_helper import open_browser, open_review, main_content, DIRECTORY_URL, SUBMITTED_CANDIDATE_ID


def test_back_to_directory():
    """RP-003: Back to Candidate Directory returns to the directory."""
    with sync_playwright() as p:
        browser, page = open_browser(p)
        open_review(page, SUBMITTED_CANDIDATE_ID)

        main_content(page).get_by_role("link", name="Back to Candidate Directory").click()
        expect(page).to_have_url(DIRECTORY_URL)
        expect(main_content(page).get_by_role("heading", name="Employee Onboarding Directory")).to_be_visible()

        browser.close()
