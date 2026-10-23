from playwright.sync_api import sync_playwright, expect
from utils.app_releases_helper import (open_browser, open_releases, page_props, current_row, form_section,
                                       form_heading, platform_radio, form_values, values)


def test_edit_from_history():
    """AR-031: Edit on the iOS Current row in History (filtered to iOS, where it's the top row) opens the same edit
    form for iOS and scrolls it into view."""
    with sync_playwright() as p:
        browser, page = open_browser(p)
        open_releases(page)
        release = page_props(page)["current"]["ios"]

        current_row(page, "ios")["row"].get_by_role("button", name="Edit").click()
        expect(form_heading(page)).to_have_text("Edit current iOS release")
        expect(platform_radio(page, "ios")).to_be_checked()
        assert form_values(page) == values(release), form_values(page)
        expect(form_section(page)).to_be_in_viewport()

        browser.close()
