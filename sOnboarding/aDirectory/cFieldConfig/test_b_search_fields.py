from playwright.sync_api import sync_playwright, expect
from utils.onboarding_helper import open_browser, open_field_config, main_content, field_rows


def test_search_fields():
    """FC-002: searching filters the fields by name."""
    with sync_playwright() as p:
        browser, page = open_browser(p)
        open_field_config(page)

        main_content(page).get_by_placeholder("Search fields...").fill("bank")
        expect(field_rows(page)).to_have_count(4)
        for name in field_rows(page).locator("td:first-child").all_inner_texts():
            assert "bank" in name.lower(), name

        browser.close()
