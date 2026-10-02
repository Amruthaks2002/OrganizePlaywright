from playwright.sync_api import sync_playwright, expect
from utils.onboarding_helper import (
    open_browser, create_candidate, new_candidate_data, open_directory, candidate_row, delete_dialog,
    delete_candidates, expect_toast, directory_empty_state,
)


def test_delete_candidate():
    """OD-035: confirming Delete removes the candidate from the directory."""
    with sync_playwright() as p:
        browser, page = open_browser(p)
        data = new_candidate_data()
        try:
            create_candidate(page, **data)
            open_directory(page, search=data["name"])
            candidate_row(page, data["name"]).get_by_role("button", name="Delete").click()
            delete_dialog(page).get_by_role("button", name="Delete", exact=True).click()
            expect_toast(page, "Onboarding record deleted successfully.")

            open_directory(page, search=data["name"])
            expect(directory_empty_state(page)).to_be_visible()
            expect(candidate_row(page, data["name"])).to_have_count(0)
        finally:
            delete_candidates(page, data["name"])

        browser.close()
