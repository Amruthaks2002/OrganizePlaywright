from playwright.sync_api import sync_playwright, expect
from utils.onboarding_helper import open_browser, open_field_config, field_row, field_switch, PROTECTED_FIELD


def test_protected_field():
    """FC-004: a protected field shows the Protected badge and its Mandatory switch can't be changed."""
    with sync_playwright() as p:
        browser, page = open_browser(p)
        open_field_config(page)

        expect(field_row(page, PROTECTED_FIELD)).to_contain_text("Protected")
        expect(field_switch(page, PROTECTED_FIELD)).to_be_disabled()

        browser.close()
