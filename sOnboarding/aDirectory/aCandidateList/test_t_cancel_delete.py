from playwright.sync_api import sync_playwright, expect
from utils.onboarding_helper import (
    open_browser, create_candidate, new_candidate_data, open_directory, candidate_row, delete_dialog,
    delete_candidates,
)


def test_cancel_delete():
    """OD-034: Delete asks for confirmation (record moves to trash), and Cancel keeps the candidate."""
    with sync_playwright() as p:
        browser, page = open_browser(p)
        data = new_candidate_data()
        try:
            create_candidate(page, **data)
            open_directory(page, search=data["name"])
            candidate_row(page, data["name"]).get_by_role("button", name="Delete").click()
            dialog = delete_dialog(page)
            expect(dialog).to_be_visible()
            expect(dialog.get_by_text("Are you sure you want to delete this onboarding record? This onboarding "
                                      "record will be moved to trash and can be restored later.")).to_be_visible()

            dialog.get_by_role("button", name="Cancel").click()
            expect(dialog).to_be_hidden()
            open_directory(page, search=data["name"])
            expect(candidate_row(page, data["name"])).to_have_count(1)
        finally:
            delete_candidates(page, data["name"])

        browser.close()
