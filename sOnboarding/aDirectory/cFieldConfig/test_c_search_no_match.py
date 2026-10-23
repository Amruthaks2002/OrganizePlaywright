from playwright.sync_api import sync_playwright, expect
from utils.onboarding_helper import open_browser, open_field_config, main_content, field_rows


def test_search_no_match():
    """FC-003: a search with no match shows the empty state."""
    with sync_playwright() as p:
        browser, page = open_browser(p)
        open_field_config(page)

        main_content(page).get_by_placeholder("Search fields...").fill("zzqa-no-such-field")
        expect(main_content(page).get_by_text("No fields configured")).to_be_visible()
        expect(main_content(page).get_by_text("There are no onboarding fields to display.")).to_be_visible()
        expect(field_rows(page)).to_have_count(0)

        browser.close()
