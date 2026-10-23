from playwright.sync_api import sync_playwright, expect
from utils.asset_helper import open_browser, unique_prefix, open_assets, main_content, select_all_box, dock, EMPTY_LIST


def test_no_results_select_all_disabled():
    """BS-009: when the search matches nothing, the Select all checkbox is disabled and no dock shows."""
    with sync_playwright() as p:
        browser, page = open_browser(p)

        open_assets(page, search=f"{unique_prefix()} nothing")
        expect(main_content(page).get_by_text(EMPTY_LIST)).to_be_visible()
        expect(select_all_box(page)).to_be_disabled()
        expect(dock(page)).to_be_hidden()

        browser.close()
