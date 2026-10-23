from playwright.sync_api import sync_playwright, expect
from utils.dashboard_helper import open_browser_as


def is_dark(page):
    return page.evaluate("document.documentElement.classList.contains('dark')")


def test_theme_toggle():
    """DB-049: the theme toggle switches between light and dark, the choice survives a reload,
    and switching back restores light mode."""
    with sync_playwright() as p:
        browser, page = open_browser_as(p, "admin")
        toggle = page.get_by_test_id("theme-toggle-button")
        assert not is_dark(page), "dashboard should start in light mode"
        expect(toggle).to_have_attribute("aria-label", "Switch to dark mode")
        try:
            toggle.click()
            page.wait_for_function("document.documentElement.classList.contains('dark')")
            expect(toggle).to_have_attribute("aria-label", "Switch to light mode")

            page.reload()
            assert is_dark(page), "dark mode was lost on reload"
        finally:
            if is_dark(page):
                page.get_by_test_id("theme-toggle-button").click()
        page.wait_for_function("!document.documentElement.classList.contains('dark')")
        expect(page.get_by_test_id("theme-toggle-button")).to_have_attribute("aria-label", "Switch to dark mode")
        browser.close()
