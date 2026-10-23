from playwright.sync_api import sync_playwright, expect
from utils.onboarding_helper import open_browser, open_directory, open_add_candidate


def test_dialog_fields():
    """OD-020: Add Candidate opens a dialog with Full Name, Personal Email, a +91 Phone Number
    (10 digits max) and an unticked Requires ESIC Registration checkbox."""
    with sync_playwright() as p:
        browser, page = open_browser(p)
        open_directory(page)
        dialog = open_add_candidate(page)

        expect(dialog.get_by_role("heading", name="Add New Onboarding Candidate")).to_be_visible()
        expect(dialog.get_by_placeholder("John Doe")).to_have_value("")
        expect(dialog.get_by_placeholder("john.doe@example.com")).to_have_attribute("type", "email")
        phone = dialog.get_by_placeholder("10-digit number")
        expect(phone).to_have_attribute("type", "tel")
        expect(phone).to_have_attribute("maxlength", "10")
        expect(dialog.get_by_text("+91")).to_be_visible()
        expect(dialog.get_by_role("checkbox", name="Requires ESIC Registration")).not_to_be_checked()
        expect(dialog.get_by_role("button", name="Cancel")).to_be_visible()
        expect(dialog.get_by_role("button", name="Save Candidate")).to_be_visible()

        browser.close()
