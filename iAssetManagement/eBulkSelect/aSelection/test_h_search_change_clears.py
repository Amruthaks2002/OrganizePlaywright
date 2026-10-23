from playwright.sync_api import sync_playwright, expect
from utils.asset_helper import (
    open_browser, unique_prefix, create_assets, delete_assets, open_assets, asset_rows, checked_rows, select_all,
    search_box, dock, expect_selected, expect_dock_counts,
)


def test_search_change_clears():
    """BS-008: narrowing the search drops the rows that are no longer shown from the selection,
    so a bulk action can never hit an asset that isn't on screen; a search that hides every
    selected row clears the selection completely."""
    with sync_playwright() as p:
        browser, page = open_browser(p)
        prefix = unique_prefix()
        try:
            names = create_assets(page, prefix)
            open_assets(page, search=prefix)
            select_all(page, 2)

            search_box(page).fill(names[0])
            page.wait_for_url(lambda url: url.endswith("%201"))
            expect(asset_rows(page)).to_have_count(1)
            expect(checked_rows(page)).to_have_count(1)
            expect_selected(page, 1)
            expect_dock_counts(page, check_in=0, check_out=1, transfer=0, delete=1)

            search_box(page).fill(f"{prefix} nothing")
            page.wait_for_url(lambda url: url.endswith("nothing"))
            expect(asset_rows(page)).to_have_count(0)
            expect(dock(page)).to_be_hidden()
        finally:
            delete_assets(page, prefix)

        browser.close()
