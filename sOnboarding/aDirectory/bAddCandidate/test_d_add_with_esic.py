from playwright.sync_api import sync_playwright, expect
from utils.onboarding_helper import (
    open_browser, create_candidate, new_candidate_data, open_directory, candidate_row, candidate_dialog,
    delete_candidates,
)


def test_add_with_esic():
    """OD-023: a candidate added with Requires ESIC Registration ticked keeps it (seen in Edit Details)."""
    with sync_playwright() as p:
        browser, page = open_browser(p)
        data = new_candidate_data()
        try:
            create_candidate(page, **data, esic=True)
            open_directory(page, search=data["name"])
            candidate_row(page, data["name"]).get_by_role("button", name="Edit Details").click()
            dialog = candidate_dialog(page, "Edit Candidate Details")
            expect(dialog.get_by_role("checkbox", name="Requires ESIC Registration")).to_be_checked()
            dialog.get_by_role("button", name="Cancel").click()
        finally:
            delete_candidates(page, data["name"])

        browser.close()
