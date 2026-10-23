from playwright.sync_api import sync_playwright, expect
from utils.asset_helper import (
    open_browser, open_assets, asset_rows, row_checkbox, checked_rows, main_content, settle, dock, expect_selected,
)


def test_page_change_clears():
    """BS-007: the selection only covers the current page - going to page 2 and back clears it.
    Read-only: nothing is submitted."""
    with sync_playwright() as p:
        browser, page = open_browser(p)

        open_assets(page)
        expect(asset_rows(page)).to_have_count(15)
        row_checkbox(asset_rows(page).first).check()
        expect_selected(page, 1)

        main_content(page).get_by_role("link", name="2", exact=True).click()
        page.wait_for_url("**/assets?page=2")
        settle(page)
        expect(dock(page)).to_be_hidden()
        expect(checked_rows(page)).to_have_count(0)

        main_content(page).get_by_role("link", name="1", exact=True).click()
        page.wait_for_url("**/assets?page=1")
        settle(page)
        expect(dock(page)).to_be_hidden()
        expect(checked_rows(page)).to_have_count(0)

        browser.close()
