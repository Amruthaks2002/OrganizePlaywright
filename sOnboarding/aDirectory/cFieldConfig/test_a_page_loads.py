from playwright.sync_api import sync_playwright, expect
from utils.onboarding_helper import (
    open_browser, open_directory, main_content, field_rows, field_counts, counts_from_switches, FIELD_CONFIG_URL,
)


def test_page_loads():
    """FC-001: Field Config (from the directory) lists every onboarding field with summary counters
    matching the switches (protected fields count as mandatory)."""
    with sync_playwright() as p:
        browser, page = open_browser(p)
        open_directory(page)
        main_content(page).get_by_role("link", name="Field Config").click()
        expect(page).to_have_url(FIELD_CONFIG_URL)
        main = main_content(page)

        expect(main.get_by_role("heading", name="Onboarding Field Configuration")).to_be_visible()
        expect(main.get_by_text("Protected fields are system-managed and cannot be modified.")).to_be_visible()
        expect(main.get_by_placeholder("Search fields...")).to_be_visible()
        for column in ["FIELD KEY", "MANDATORY", "STATUS"]:
            expect(main.locator("thead")).to_contain_text(column, ignore_case=True)
        expect(field_rows(page).first).to_be_visible()
        mandatory, optional, protected = field_counts(page)
        assert mandatory + optional == field_rows(page).count(), (field_counts(page), field_rows(page).count())
        assert field_counts(page) == counts_from_switches(page), (field_counts(page), counts_from_switches(page))

        browser.close()
