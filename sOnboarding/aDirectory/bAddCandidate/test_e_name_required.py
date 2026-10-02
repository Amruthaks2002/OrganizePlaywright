from playwright.sync_api import sync_playwright, expect
from utils.onboarding_helper import (
    open_browser, open_directory, open_add_candidate, fill_candidate_form, new_candidate_data, candidate_rows,
    delete_candidates,
)


def test_name_required():
    """OD-024: Save Candidate with Full Name empty is blocked and nothing is created."""
    with sync_playwright() as p:
        browser, page = open_browser(p)
        data = new_candidate_data()
        try:
            open_directory(page)
            dialog = open_add_candidate(page)
            fill_candidate_form(dialog, **{**data, "name": ""})
            dialog.get_by_role("button", name="Save Candidate").click()
            page.wait_for_timeout(1500)

            expect(dialog).to_be_visible()
            field = dialog.get_by_placeholder("John Doe")
            assert field.evaluate("e => !e.checkValidity()"), "Full Name should be flagged as missing"

            dialog.get_by_role("button", name="Cancel").click()
            open_directory(page, search=data["email"])
            expect(candidate_rows(page)).to_have_count(0)
        finally:
            delete_candidates(page, data["email"])

        browser.close()
