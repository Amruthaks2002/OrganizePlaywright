from playwright.sync_api import sync_playwright, expect
from utils.onboarding_helper import open_browser, open_journeys, open_create_journey, fill_journey_form, JOURNEYS_URL


def test_blank_name():
    """OJ-010: a name of only spaces is rejected as missing."""
    with sync_playwright() as p:
        browser, page = open_browser(p)
        open_journeys(page)
        dialog = open_create_journey(page)

        fill_journey_form(page, dialog, "   ")
        dialog.get_by_role("button", name="Create Journey").click()
        expect(dialog.get_by_text("The name field is required.")).to_be_visible()
        expect(page).to_have_url(JOURNEYS_URL)

        browser.close()
