from playwright.sync_api import sync_playwright, expect
from utils.onboarding_helper import (
    open_browser, open_directory, open_add_candidate, fill_candidate_form, new_candidate_data, candidate_row,
    delete_candidates,
)


def test_add_candidate():
    """OD-022: saving a valid candidate closes the dialog and lists them as a new In Progress candidate.

    Known bug: saving shows "Onboarding invitation template not found." and the dialog stays
    open, although the candidate is created. This test fails until that's fixed.
    """
    with sync_playwright() as p:
        browser, page = open_browser(p)
        data = new_candidate_data()
        try:
            open_directory(page)
            dialog = open_add_candidate(page)
            fill_candidate_form(dialog, **data)
            dialog.get_by_role("button", name="Save Candidate").click()
            page.wait_for_timeout(2000)
            expect(page.get_by_text("Onboarding invitation template not found.")).to_have_count(0)
            expect(dialog, "the dialog should close after saving").to_be_hidden()

            open_directory(page, search=data["name"], status="in_progress")
            row = candidate_row(page, data["name"])
            expect(row).to_have_count(1)
            for text in ["Fresher (0 yrs)", f"+91{data['phone']}", data["email"], "Not Assigned", "Joining: Pending",
                         "In Progress"]:
                expect(row).to_contain_text(text)
            expect(row.get_by_role("button", name="Edit Details")).to_be_visible()
        finally:
            page.keyboard.press("Escape")
            delete_candidates(page, data["name"])

        browser.close()
