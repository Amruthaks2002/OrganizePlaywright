from playwright.sync_api import sync_playwright, expect
from utils.marketplace_helper import (
    open_browser, unique_name, create_live_app, delete_apps, open_app, kudos_button, stat, app_data, page_props,
    show_url,
)


def test_kudos_toggle():
    """MP-030: 'Give kudos' adds one kudos and turns into 'Kudos given'; clicking it again takes
    the kudos back."""
    with sync_playwright() as p:
        browser, page = open_browser(p)
        name = unique_name()
        try:
            create_live_app(page, name)
            open_app(page, name)
            expect(kudos_button(page)).to_have_text("Give kudos")
            assert stat(page, "Kudos") == 0

            kudos_button(page).click()
            expect(kudos_button(page)).to_have_text("Kudos given")
            assert stat(page, "Kudos") == 1
            assert app_data(page, name)["kudos_count"] == 1
            assert page_props(page, show_url(name))["hasKudoed"] is True

            kudos_button(page).click()
            expect(kudos_button(page)).to_have_text("Give kudos")
            assert stat(page, "Kudos") == 0
            assert app_data(page, name)["kudos_count"] == 0
        finally:
            delete_apps(page, name)

        browser.close()
