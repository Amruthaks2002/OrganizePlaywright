from playwright.sync_api import sync_playwright, expect
from utils.onboarding_helper import (
    open_browser, create_candidate, open_directory, open_add_candidate, fill_candidate_form, new_candidate_data,
    candidate_rows, delete_candidates, unique_tag,
)


def test_duplicate_email():
    """OD-031: a second candidate with an existing email is rejected."""
    with sync_playwright() as p:
        browser, page = open_browser(p)
        tag = unique_tag()
        first = new_candidate_data(tag)
        second = {**new_candidate_data(), "name": f"{first['name']} Dup", "email": first["email"]}
        try:
            create_candidate(page, **first)
            open_directory(page)
            dialog = open_add_candidate(page)
            fill_candidate_form(dialog, **second)
            dialog.get_by_role("button", name="Save Candidate").click()
            expect(dialog.get_by_text("The personal email has already been taken.")).to_be_visible()

            dialog.get_by_role("button", name="Cancel").click()
            open_directory(page, search=tag)
            expect(candidate_rows(page)).to_have_count(1)
        finally:
            delete_candidates(page, tag)

        browser.close()
