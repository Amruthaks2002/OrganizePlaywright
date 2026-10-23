import re
from playwright.sync_api import sync_playwright, expect
from utils.onboarding_helper import open_browser, open_review, main_content, SUBMITTED_CANDIDATE_ID


def test_approve_selected_disabled():
    """RP-004: Approve Selected (0) is disabled while nothing is selected."""
    with sync_playwright() as p:
        browser, page = open_browser(p)
        open_review(page, SUBMITTED_CANDIDATE_ID)

        buttons = main_content(page).get_by_role("button", name=re.compile("Approve Selected", re.I))
        expect(buttons).to_have_count(2)
        for i in range(2):
            expect(buttons.nth(i)).to_have_text(re.compile(r"Approve Selected \(0\)", re.I))
            expect(buttons.nth(i)).to_be_disabled()

        browser.close()
