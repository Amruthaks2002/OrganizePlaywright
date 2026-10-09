from playwright.sync_api import sync_playwright, expect
from utils.marketplace_helper import (
    open_browser, unique_name, create_app, delete_apps, open_app, main_content, MARKETPLACE_URL,
)


def test_form_prefilled():
    """MP-038: Edit opens the form filled with the app's saved details."""
    with sync_playwright() as p:
        browser, page = open_browser(p)
        name = unique_name()
        try:
            app_id = create_app(page, name, platform="macos", category="Reporting", short_description="Prefilled summary.",
                                description="Prefilled full description.", tags="alpha, beta",
                                external_url="https://example.com/prefilled", version="4.0.0", min_os_version="14.0")
            open_app(page, name)
            main_content(page).get_by_role("link", name="Edit", exact=True).click()
            page.wait_for_url(f"{MARKETPLACE_URL}/{app_id}/edit")
            expect(main_content(page).get_by_role("heading", name=f"Edit {name}")).to_be_visible()

            expect(page.locator("#name")).to_have_value(name)
            expect(page.locator("#short_description")).to_have_value("Prefilled summary.")
            expect(page.locator(".html-editor-content")).to_contain_text("Prefilled full description.")
            expect(page.locator("#category")).to_have_value("Reporting")
            expect(page.locator("#tags")).to_have_value("alpha, beta")
            expect(page.locator("#external_url")).to_have_value("https://example.com/prefilled")
            expect(page.locator("#version")).to_have_value("4.0.0")
            expect(page.locator("#min_os_version")).to_have_value("14.0")
            expect(page.locator("#host_app")).to_have_count(0)
        finally:
            delete_apps(page, name)

        browser.close()
