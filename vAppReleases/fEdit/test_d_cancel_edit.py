from playwright.sync_api import sync_playwright, expect
from utils.app_releases_helper import (open_browser, page_props, reload_props, current_releases, open_edit_from_card,
                                       fill_form, cancel_edit_button, form_heading, platform_radio, publish_button,
                                       form_values, values, is_release_request)


def test_cancel_edit():
    """AR-033: Cancel leaves edit mode without saving: the form is back to Publish a release with both platforms
    selectable, and what was typed is dropped."""
    with sync_playwright() as p:
        browser, page = open_browser(p)
        snapshot = current_releases(page)
        total = page_props(page)["history"]["total"]
        sent = []
        page.on("request", lambda r: sent.append(r.url) if is_release_request(r) else None)

        open_edit_from_card(page, "android")
        fill_form(page, optional_message="AR-033 not saved")
        cancel_edit_button(page).click()

        expect(form_heading(page)).to_have_text("Publish a release")
        for platform in ["android", "ios"]:
            expect(platform_radio(page, platform)).to_be_enabled()
        expect(publish_button(page)).to_be_visible()
        assert form_values(page) == values(snapshot["android"]), form_values(page)
        assert sent == [], sent
        after = reload_props(page)
        assert (after["current"], after["history"]["total"]) == (snapshot, total)

        browser.close()
