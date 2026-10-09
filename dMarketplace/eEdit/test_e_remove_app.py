from playwright.sync_api import sync_playwright, expect
from utils.marketplace_helper import (
    open_browser, unique_name, create_live_app, delete_apps, open_app, main_content, answer_next_dialog,
    expect_toast, app_data, search_app_names, show_url, MARKETPLACE_URL,
)

CONFIRM = "Remove this app from the marketplace? This cannot be undone."


def test_remove_app():
    """MP-042: Remove asks for confirmation; dismissing keeps the app, accepting deletes it for
    good (its page is gone and it's no longer listed)."""
    with sync_playwright() as p:
        browser, page = open_browser(p)
        name = unique_name()
        try:
            create_live_app(page, name)
            open_app(page, name)
            remove = main_content(page).get_by_role("button", name="Remove", exact=True)

            messages = answer_next_dialog(page, accept=False)
            remove.click()
            page.wait_for_timeout(1000)
            assert messages == [CONFIRM], messages
            assert app_data(page, name) is not None, "dismissing the confirmation must keep the app"

            messages = answer_next_dialog(page, accept=True)
            remove.click()
            expect_toast(page, "Website removed from the marketplace.")
            page.wait_for_url(MARKETPLACE_URL)
            assert messages == [CONFIRM], messages
            assert page.request.get(show_url(name)).status == 404
            assert search_app_names(page, name, mine=True) == []
        finally:
            delete_apps(page, name)

        browser.close()
