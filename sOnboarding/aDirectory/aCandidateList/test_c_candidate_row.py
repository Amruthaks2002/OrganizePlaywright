from playwright.sync_api import sync_playwright, expect
from utils.onboarding_helper import open_browser, open_directory, candidate_row, review_url, SUBMITTED_CANDIDATE_ID


def test_candidate_row():
    """OD-003: a candidate row shows name, experience, phone, email, designation, joining date,
    status, last activity and the row actions."""
    with sync_playwright() as p:
        browser, page = open_browser(p)
        open_directory(page, search="maju")

        row = candidate_row(page, "maju")
        expect(row).to_have_count(1)
        for text in ["1 yrs exp", "+917878789999", "maju@gmail.com", "hfghfg", "Joining: Aug 26, 2026",
                     "Submitted", "Aug 14, 10:52 AM"]:
            expect(row).to_contain_text(text)
        expect(row.get_by_role("button", name="Delete")).to_be_visible()
        expect(row.get_by_role("link", name="Review Profile")).to_have_attribute(
            "href", review_url(SUBMITTED_CANDIDATE_ID))

        browser.close()
