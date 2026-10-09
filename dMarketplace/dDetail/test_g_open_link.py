from playwright.sync_api import sync_playwright, expect
from utils.marketplace_helper import open_browser, unique_name, create_live_app, delete_apps, open_app, main_content


def test_open_link():
    """MP-036: a linked app's 'Open' button points at its external link and opens it in a new tab."""
    with sync_playwright() as p:
        browser, page = open_browser(p)
        name = unique_name()
        url = "https://example.com/qa-open-link"
        try:
            create_live_app(page, name, external_url=url)
            open_app(page, name)
            link = main_content(page).get_by_role("link", name="Open", exact=True)
            expect(link).to_have_attribute("href", url)
            expect(link).to_have_attribute("target", "_blank")
            expect(main_content(page).get_by_role("link", name="Download", exact=True)).to_have_count(0)
        finally:
            delete_apps(page, name)

        browser.close()
