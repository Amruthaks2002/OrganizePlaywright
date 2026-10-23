import re

from playwright.sync_api import sync_playwright, expect
from utils.app_releases_helper import (open_browser, open_releases, page_props, open_edit_from_card, form_section,
                                       form_heading, platform_radio, form_values, values, save_button,
                                       publish_button, cancel_edit_button, published_text)


def test_edit_from_card():
    """AR-030: Edit on the Android card turns the form into 'Edit current Android release': it explains the release
    is changed in place, is outlined in amber, locks the platform on Android, holds the release's values and offers
    Save changes / Cancel instead of Publish release."""
    with sync_playwright() as p:
        browser, page = open_browser(p)
        open_releases(page)
        release = page_props(page)["current"]["android"]

        open_edit_from_card(page, "android")
        expect(form_heading(page)).to_have_text("Edit current Android release")
        expect(form_section(page).get_by_text(
            f"Fixing a mistake in the release published {published_text(release['created_at'])}. "
            "It is changed in place.")).to_be_visible()
        expect(form_section(page)).to_have_class(re.compile(r"\bborder-amber-300\b"))
        expect(platform_radio(page, "android")).to_be_checked()
        for platform in ["android", "ios"]:
            expect(platform_radio(page, platform)).to_be_disabled()
        assert form_values(page) == values(release), form_values(page)
        expect(save_button(page)).to_be_visible()
        expect(cancel_edit_button(page)).to_be_visible()
        expect(publish_button(page)).to_have_count(0)

        browser.close()
