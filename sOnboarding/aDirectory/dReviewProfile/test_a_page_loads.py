import re
from playwright.sync_api import sync_playwright, expect
from utils.onboarding_helper import (
    open_browser, open_review, main_content, review_counters, global_status, nav_button, history_url,
    SUBMITTED_CANDIDATE_ID,
)

SECTIONS = ["Basic Information", "Family & Emergency Contacts", "Address Details", "Bank & Government Details",
            "Previous Employment Details", "Academic Certificates", "Government Identity & Documents",
            "Previous Employment Documents", "Passport Photograph", "Bank Account Details Document"]


def test_page_loads():
    """RP-001: the review page shows the candidate, View History, the global status, the
    approved / correction / pending counters and the section navigation with Basic Information open."""
    with sync_playwright() as p:
        browser, page = open_browser(p)
        open_review(page, SUBMITTED_CANDIDATE_ID)
        main = main_content(page)

        expect(main.get_by_role("link", name="Back to Candidate Directory")).to_be_visible()
        expect(main.get_by_role("heading", name="maju")).to_be_visible()
        expect(main.get_by_text("+917878789999").first).to_be_visible()
        expect(main.get_by_role("link", name="View History")).to_have_attribute("href", history_url(SUBMITTED_CANDIDATE_ID))
        assert global_status(page) == "SUBMITTED", global_status(page)
        approved, correction, pending = review_counters(page)
        assert approved + correction + pending > 0
        expect(main.get_by_text("Select All Pending Items")).to_be_visible()
        for section in SECTIONS:
            expect(nav_button(page, section)).to_be_visible()
        expect(main.locator("main section h3").first).to_have_text(re.compile("Basic Information", re.I))

        browser.close()
