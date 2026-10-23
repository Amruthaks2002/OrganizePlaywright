from playwright.sync_api import sync_playwright, expect
from utils.app_releases_helper import (open_browser, open_releases, page_props, fill_form, publish_button,
                                       confirm_dialog, dialog_title, dialog_message, dialog_buttons, bump)


def test_publish_confirmation():
    """AR-009: Publish release first asks 'Publish Android release?' with the latest / minimum it will set."""
    with sync_playwright() as p:
        browser, page = open_browser(p)
        open_releases(page)
        release = page_props(page)["current"]["android"]
        latest, minimum = bump(release["latest_version"]), release["min_version"]

        fill_form(page, "android", latest_version=latest)
        publish_button(page).click()
        expect(dialog_title(page)).to_have_text("Publish Android release?")
        expect(dialog_message(page)).to_have_text(
            f"Latest {latest}, minimum {minimum}. Installs below {minimum} will be blocked until they update.")
        assert dialog_buttons(page) == ["Cancel", "Publish"], dialog_buttons(page)

        confirm_dialog(page).get_by_role("button", name="Cancel", exact=True).click()
        expect(confirm_dialog(page)).to_have_count(0)

        browser.close()
