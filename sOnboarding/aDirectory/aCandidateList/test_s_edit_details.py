from playwright.sync_api import sync_playwright, expect
from utils.onboarding_helper import (
    open_browser, create_candidate, new_candidate_data, open_directory, candidate_row, candidate_dialog,
    fill_candidate_form, delete_candidates, unique_tag,
)


def test_edit_details():
    """OD-019: Edit Details opens the candidate prefilled, and saving updates the row and closes the dialog.

    Known bug: saving shows "Onboarding invitation template not found." and the dialog stays
    open (the change is saved anyway). This test fails until that's fixed.
    """
    with sync_playwright() as p:
        browser, page = open_browser(p)
        tag = unique_tag()
        data = new_candidate_data(tag)
        new_name = f"{data['name']} Edited"
        try:
            create_candidate(page, **data)
            open_directory(page, search=data["name"])
            candidate_row(page, data["name"]).get_by_role("button", name="Edit Details").click()
            dialog = candidate_dialog(page, "Edit Candidate Details")
            expect(dialog).to_be_visible()
            expect(dialog.get_by_placeholder("John Doe")).to_have_value(data["name"])
            expect(dialog.get_by_placeholder("john.doe@example.com")).to_have_value(data["email"])
            expect(dialog.get_by_placeholder("10-digit number")).to_have_value(data["phone"])

            fill_candidate_form(dialog, name=new_name)
            dialog.get_by_role("button", name="Save Candidate").click()
            expect(page.get_by_text("Onboarding invitation template not found.")).to_have_count(0, timeout=3000)
            expect(dialog, "the dialog should close after saving").to_be_hidden()

            open_directory(page, search=tag)
            expect(candidate_row(page, new_name)).to_have_count(1)
        finally:
            page.keyboard.press("Escape")
            delete_candidates(page, tag)

        browser.close()
