from playwright.sync_api import sync_playwright, expect
from utils.app_releases_helper import (open_browser, open_releases, page_props, fill_form, publish_button,
                                       confirm_dialog, dialog_title, dialog_message, dialog_buttons, lower)


def test_lower_minimum_warning():
    """AR-010: lowering the minimum warns that blocked installs will be let back in, with a 'Lower minimum' button."""
    with sync_playwright() as p:
        browser, page = open_browser(p)
        open_releases(page)
        old = page_props(page)["current"]["android"]["min_version"]
        new = lower(old)

        fill_form(page, "android", min_version=new)
        publish_button(page).click()
        expect(dialog_title(page)).to_have_text("Publish Android release?")
        expect(dialog_message(page)).to_have_text(
            f"This lowers the minimum from {old} to {new}. "
            f"Installs between {new} and {old} that are blocked now will be allowed again.")
        assert dialog_buttons(page) == ["Cancel", "Lower minimum"], dialog_buttons(page)

        confirm_dialog(page).get_by_role("button", name="Cancel", exact=True).click()
        expect(confirm_dialog(page)).to_have_count(0)

        browser.close()
