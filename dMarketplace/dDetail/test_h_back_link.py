from playwright.sync_api import sync_playwright
from utils.marketplace_helper import (
    open_browser, unique_name, create_live_app, delete_apps, open_app, open_marketplace, main_content, MARKETPLACE_URL,
)


def test_back_link():
    """MP-037: '← Marketplace' on an app's page goes back to the marketplace list."""
    with sync_playwright() as p:
        browser, page = open_browser(p)
        name = unique_name()
        try:
            create_live_app(page, name)
            open_app(page, name)
            main_content(page).get_by_role("link", name="← Marketplace").click()
            page.wait_for_url(MARKETPLACE_URL)
            open_marketplace(page)
        finally:
            delete_apps(page, name)

        browser.close()
