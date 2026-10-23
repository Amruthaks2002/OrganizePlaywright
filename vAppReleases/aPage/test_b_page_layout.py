from playwright.sync_api import sync_playwright, expect
from utils.app_releases_helper import (open_browser, open_releases, card, form_heading, history_section,
                                       history_select, publish_button, PLATFORMS)


def test_page_layout():
    """AR-002: the page shows an Android and an iOS card, the Publish a release form and the History table."""
    with sync_playwright() as p:
        browser, page = open_browser(p)
        open_releases(page)

        for platform in PLATFORMS:
            expect(card(page, platform)).to_be_visible()
        expect(form_heading(page)).to_have_text("Publish a release")
        expect(publish_button(page)).to_be_visible()
        expect(history_section(page).locator("table")).to_be_visible()
        expect(history_select(page)).to_be_visible()

        browser.close()
