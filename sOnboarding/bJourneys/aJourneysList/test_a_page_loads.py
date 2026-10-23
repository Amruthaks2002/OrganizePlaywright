import re
from playwright.sync_api import sync_playwright, expect
from utils.onboarding_helper import open_browser, open_onboarding_submenu, main_content, journey_stats, JOURNEYS_URL


def test_page_loads():
    """OJ-001: Onboarding > Journeys opens the journeys page with Create Journey and the summary counters."""
    with sync_playwright() as p:
        browser, page = open_browser(p)
        open_onboarding_submenu(page, "journeys")
        main = main_content(page)

        expect(page).to_have_url(JOURNEYS_URL)
        expect(main.get_by_role("heading", name="Onboarding Journeys")).to_be_visible()
        expect(main.get_by_text("Create and manage onboarding journeys for new employees.")).to_be_visible()
        expect(main.get_by_role("button", name="Create Journey")).to_be_visible()
        for label in ["Total Journeys", "Active", "Total Steps"]:
            expect(main.get_by_text(label, exact=True).first).to_be_visible()
        journey_stats(page)
        expect(main.get_by_role("link", name="Manage Steps").first).to_be_visible()

        browser.close()
