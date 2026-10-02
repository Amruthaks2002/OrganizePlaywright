from playwright.sync_api import sync_playwright, expect
from utils.onboarding_helper import (
    open_browser, open_directory, open_add_candidate, fill_candidate_form, new_candidate_data, candidate_rows,
    delete_candidates, unique_tag,
)


def test_invalid_email():
    """OD-027: an email without a proper domain (name@domain, no TLD) is rejected and nothing is created.

    Known bug: the browser lets "x@hshsj" through and the server accepts it (the directory
    already holds such records, e.g. "hari@hshsj"). This test fails until that's fixed.
    """
    with sync_playwright() as p:
        browser, page = open_browser(p)
        tag = unique_tag()
        data = {**new_candidate_data(tag), "email": f"qa.{tag}@hshsj"}
        try:
            open_directory(page)
            dialog = open_add_candidate(page)
            fill_candidate_form(dialog, **data)
            dialog.get_by_role("button", name="Save Candidate").click()
            page.wait_for_timeout(2500)
            expect(dialog).to_be_visible()

            dialog.get_by_role("button", name="Cancel").click()
            open_directory(page, search=data["name"])
            expect(candidate_rows(page), "a candidate with an invalid email was created").to_have_count(0)
        finally:
            page.keyboard.press("Escape")
            delete_candidates(page, tag)

        browser.close()
