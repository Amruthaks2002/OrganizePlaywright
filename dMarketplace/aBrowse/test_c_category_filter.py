import re

from playwright.sync_api import sync_playwright, expect
from utils.marketplace_helper import (
    open_browser, unique_name, create_live_app, delete_apps, open_marketplace, category_select, card_names,
)


def test_category_filter():
    """MP-003: picking a category lists only that category's apps."""
    with sync_playwright() as p:
        browser, page = open_browser(p)
        prefix = unique_name()
        reporting, hr = f"{prefix} Reporting", f"{prefix} HR"
        try:
            create_live_app(page, reporting, category="Reporting")
            create_live_app(page, hr, category="HR tools")
            open_marketplace(page, search=prefix)
            assert sorted(card_names(page)) == sorted([reporting, hr]), card_names(page)

            category_select(page).select_option("Reporting")
            page.wait_for_url(re.compile(r"category=Reporting"))
            expect(page.get_by_test_id("main-content").get_by_role("heading", name=hr)).to_have_count(0)
            assert card_names(page) == [reporting], card_names(page)

            category_select(page).select_option("HR tools")
            page.wait_for_url(re.compile(r"category=HR(\+|%20)tools"))
            expect(page.get_by_test_id("main-content").get_by_role("heading", name=reporting)).to_have_count(0)
            assert card_names(page) == [hr], card_names(page)
        finally:
            delete_apps(page, reporting, hr)

        browser.close()
