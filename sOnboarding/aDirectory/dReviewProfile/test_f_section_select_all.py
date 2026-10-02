import re
from playwright.sync_api import sync_playwright, expect
from utils.onboarding_helper import open_browser, open_review, current_section, section_approve_selected, SUBMITTED_CANDIDATE_ID


def test_section_select_all():
    """RP-006: the section's Select All ticks every pending field in that section (nothing is approved)."""
    with sync_playwright() as p:
        browser, page = open_browser(p)
        open_review(page, SUBMITTED_CANDIDATE_ID)
        section = current_section(page)
        checkboxes = section.locator("div.divide-y input[type=checkbox]")
        expect(checkboxes).to_have_count(10)

        section.get_by_text("Select All", exact=True).click()
        for i in range(10):
            expect(checkboxes.nth(i)).to_be_checked()
        expect(section_approve_selected(page)).to_have_text(re.compile(r"Approve Selected \(10\)", re.I))

        section.get_by_text("Select All", exact=True).click()
        expect(section_approve_selected(page)).to_have_text(re.compile(r"Approve Selected \(0\)", re.I))

        browser.close()
