import re
from playwright.sync_api import sync_playwright, expect
from utils.onboarding_helper import open_browser, open_review, main_content, review_row, SUBMITTED_CANDIDATE_ID


def test_select_one_field():
    """RP-005: ticking a pending field enables Approve Selected with a count of 1 (nothing is approved)."""
    with sync_playwright() as p:
        browser, page = open_browser(p)
        open_review(page, SUBMITTED_CANDIDATE_ID)
        buttons = main_content(page).get_by_role("button", name=re.compile("Approve Selected", re.I))

        checkbox = review_row(page, "Designation").locator("input[type=checkbox]")
        checkbox.check()
        for i in range(2):
            expect(buttons.nth(i)).to_have_text(re.compile(r"Approve Selected \(1\)", re.I))
            expect(buttons.nth(i)).to_be_enabled()

        checkbox.uncheck()
        expect(buttons.first).to_have_text(re.compile(r"Approve Selected \(0\)", re.I))
        expect(buttons.first).to_be_disabled()

        browser.close()
