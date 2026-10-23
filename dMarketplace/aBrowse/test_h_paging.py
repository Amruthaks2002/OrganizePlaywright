import re

from playwright.sync_api import sync_playwright, expect
from utils.marketplace_helper import (
    open_browser, unique_name, create_live_app, delete_apps, open_marketplace, card_names, result_count,
    main_content, PAGE_SIZE,
)


def test_paging():
    """MP-008: the list shows 12 apps a page; the rest are on page 2, with no app on both pages."""
    with sync_playwright() as p:
        browser, page = open_browser(p)
        prefix = unique_name()
        names = [f"{prefix} {i:02d}" for i in range(1, PAGE_SIZE + 2)]
        try:
            for name in names:
                create_live_app(page, name)

            open_marketplace(page, search=prefix)
            expect(result_count(page)).to_have_text(f"{len(names)} results")
            first = card_names(page)
            assert len(first) == PAGE_SIZE, first

            main_content(page).locator("a[href*='page=2']:visible", has_text="2").first.click()
            page.wait_for_url(re.compile(r"[?&]page=2\b"))
            expect(main_content(page).locator("a h2")).to_have_count(1)
            second = card_names(page)
            assert sorted(first + second) == sorted(names), first + second
        finally:
            delete_apps(page, *names)

        browser.close()
