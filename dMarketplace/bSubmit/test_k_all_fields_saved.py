from playwright.sync_api import sync_playwright, expect
from utils.marketplace_helper import (
    open_browser, unique_name, submit_new_app, delete_apps, main_content, app_data,
)


def test_all_fields_saved():
    """MP-020: everything entered on the form shows on the detail page: platform, category,
    summary, full description, tags, link, version and minimum OS."""
    with sync_playwright() as p:
        browser, page = open_browser(p)
        name = unique_name()
        url = "https://example.com/qa-all-fields"
        try:
            submit_new_app(page, name, platform="macos", short="All fields summary.",
                           description="All fields full description.", category="Reporting",
                           tags="alpha, beta", url=url, version="3.1.4", min_os="13.0")
            main = main_content(page)
            for text in ["by Admin User", "macOS app", "Reporting", "All fields summary.", "All fields full description.",
                         "3.1.4", "13.0"]:
                expect(main).to_contain_text(text)
            for tag in ["alpha", "beta"]:
                expect(main.get_by_text(tag, exact=True)).to_be_visible()
            expect(main.get_by_role("link", name="Open", exact=True)).to_have_attribute("href", url)

            data = app_data(page, name)
            assert (data["category"], data["tags"], data["version"], data["min_os_version"]) == \
                ("Reporting", ["alpha", "beta"], "3.1.4", "13.0"), data
        finally:
            delete_apps(page, name)

        browser.close()
