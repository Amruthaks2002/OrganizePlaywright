from playwright.sync_api import sync_playwright, expect
from utils.onboarding_helper import (
    open_browser, open_directory, open_add_candidate, fill_candidate_form, new_candidate_data, candidate_rows,
    delete_candidates,
)


def test_cancel_add():
    """OD-021: Cancel closes the Add Candidate dialog without creating the candidate."""
    with sync_playwright() as p:
        browser, page = open_browser(p)
        data = new_candidate_data()
        try:
            open_directory(page)
            dialog = open_add_candidate(page)
            fill_candidate_form(dialog, **data)
            dialog.get_by_role("button", name="Cancel").click()
            expect(dialog).to_be_hidden()

            open_directory(page, search=data["name"])
            expect(candidate_rows(page)).to_have_count(0)
        finally:
            delete_candidates(page, data["name"])

        browser.close()
