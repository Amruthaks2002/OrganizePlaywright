from playwright.sync_api import sync_playwright, expect
from utils.onboarding_helper import open_browser, open_journeys, open_create_journey, is_active_on


def test_create_dialog_fields():
    """OJ-004: Create Journey opens a dialog with a required name, an optional designation picker,
    a description and the Active switch (on by default)."""
    with sync_playwright() as p:
        browser, page = open_browser(p)
        open_journeys(page)
        dialog = open_create_journey(page)

        expect(dialog.get_by_role("heading", name="Create Onboarding Journey")).to_be_visible()
        expect(dialog.get_by_text("Journey Name *")).to_be_visible()
        expect(dialog.get_by_placeholder("e.g., Software Engineer Onboarding")).to_have_value("")
        expect(dialog.get_by_text("Leave blank to make this journey available to all employees")).to_be_visible()
        expect(dialog.get_by_placeholder("Select Designation")).to_be_visible()
        expect(dialog.get_by_placeholder("Briefly describe the purpose of this journey...")).to_have_value("")
        expect(dialog.get_by_text("This journey will be available for assignment.")).to_be_visible()
        assert is_active_on(dialog), "Active should be on by default"
        expect(dialog.get_by_role("button", name="Cancel")).to_be_visible()
        expect(dialog.get_by_role("button", name="Create Journey")).to_be_visible()

        browser.close()
