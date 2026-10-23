from playwright.sync_api import sync_playwright, expect
from utils.onboarding_helper import open_browser, open_journeys, open_create_journey, vue_select


def test_clear_designation():
    """OJ-013: Clear Selected removes the chosen designation (back to all employees)."""
    with sync_playwright() as p:
        browser, page = open_browser(p)
        open_journeys(page)
        dialog = open_create_journey(page)

        vue_select(page, dialog, "Select Designation", "Business Analyst")
        expect(dialog.locator(".vs__selected")).to_have_text("Business Analyst")

        dialog.get_by_role("button", name="Clear Selected").click()
        expect(dialog.locator(".vs__selected")).to_have_count(0)
        expect(dialog.get_by_placeholder("Select Designation")).to_be_visible()

        browser.close()
