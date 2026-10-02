from playwright.sync_api import sync_playwright, expect
from utils.onboarding_helper import open_browser, open_onboarding_submenu, SIDEBAR_CHILDREN


def test_sidebar_menu():
    """OD-002: the Onboarding sidebar group lists Directory, Journeys, Journey Progress and OCR Analytics,
    and each one opens its page."""
    with sync_playwright() as p:
        browser, page = open_browser(p)
        page.get_by_test_id("sidebar-parent-onboarding").click()
        for child in SIDEBAR_CHILDREN:
            expect(page.get_by_test_id(f"sidebar-child-{child}")).to_be_visible()

        for child, url in SIDEBAR_CHILDREN.items():
            open_onboarding_submenu(page, child)
            expect(page).to_have_url(url)

        browser.close()
