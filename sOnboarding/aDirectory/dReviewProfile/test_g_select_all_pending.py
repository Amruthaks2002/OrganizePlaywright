import re
from playwright.sync_api import sync_playwright, expect
from utils.onboarding_helper import open_browser, open_review, main_content, review_counters, SUBMITTED_CANDIDATE_ID


def test_select_all_pending():
    """RP-007: Select All Pending Items selects every pending field across all sections
    (the count matches the Pending counter; nothing is approved)."""
    with sync_playwright() as p:
        browser, page = open_browser(p)
        open_review(page, SUBMITTED_CANDIDATE_ID)
        main = main_content(page)
        pending = review_counters(page)[2]
        top_button = main.get_by_role("button", name=re.compile("Approve Selected", re.I)).first

        main.get_by_text("Select All Pending Items").click()
        expect(top_button).to_have_text(re.compile(rf"Approve Selected \({pending}\)", re.I))
        expect(top_button).to_be_enabled()

        main.get_by_text("Select All Pending Items").click()
        expect(top_button).to_have_text(re.compile(r"Approve Selected \(0\)", re.I))

        browser.close()
