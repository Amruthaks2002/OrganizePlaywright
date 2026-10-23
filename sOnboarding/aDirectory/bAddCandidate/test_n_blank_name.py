from playwright.sync_api import sync_playwright, expect
from utils.onboarding_helper import (
    open_browser, open_directory, open_add_candidate, fill_candidate_form, new_candidate_data, candidate_rows,
    delete_candidates,
)


def test_blank_name():
    """OD-032: a name of only spaces is rejected as missing."""
    with sync_playwright() as p:
        browser, page = open_browser(p)
        data = {**new_candidate_data(), "name": "   "}
        try:
            open_directory(page)
            dialog = open_add_candidate(page)
            fill_candidate_form(dialog, **data)
            dialog.get_by_role("button", name="Save Candidate").click()
            expect(dialog.get_by_text("The name field is required.")).to_be_visible()

            dialog.get_by_role("button", name="Cancel").click()
            open_directory(page, search=data["email"])
            expect(candidate_rows(page)).to_have_count(0)
        finally:
            delete_candidates(page, data["email"])

        browser.close()
