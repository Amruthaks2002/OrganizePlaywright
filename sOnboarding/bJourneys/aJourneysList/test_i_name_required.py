from playwright.sync_api import sync_playwright, expect
from utils.onboarding_helper import open_browser, open_journeys, open_create_journey, fill_journey_form, JOURNEYS_URL


def test_name_required():
    """OJ-009: Create Journey with no name is blocked."""
    with sync_playwright() as p:
        browser, page = open_browser(p)
        open_journeys(page)
        dialog = open_create_journey(page)

        fill_journey_form(page, dialog, description="no name")
        dialog.get_by_role("button", name="Create Journey").click()
        page.wait_for_timeout(1500)
        expect(dialog).to_be_visible()
        assert dialog.get_by_placeholder("e.g., Software Engineer Onboarding").evaluate("e => !e.checkValidity()")
        expect(page).to_have_url(JOURNEYS_URL)

        browser.close()
