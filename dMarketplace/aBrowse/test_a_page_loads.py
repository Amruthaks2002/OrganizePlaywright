from playwright.sync_api import sync_playwright, expect
from utils.marketplace_helper import (
    open_browser, open_marketplace, main_content, search_box, category_select, sort_select, platform_chip,
    mine_switch, result_count, PLATFORMS, CATEGORIES, SORTS, REVIEW_URL, TRENDS_URL, CREATE_URL,
)


def test_page_loads():
    """MP-001: the marketplace opens from the sidebar with its header links, search, category and
    sort pickers, the platform chips and a results count."""
    with sync_playwright() as p:
        browser, page = open_browser(p)

        page.get_by_test_id("sidebar-navlink-marketplace").click()
        page.wait_for_url("**/marketplace")
        open_marketplace(page)
        main = main_content(page)

        expect(main.get_by_text("Apps, tools, plugins and ideas built by your colleagues.")).to_be_visible()
        expect(main.get_by_role("link", name="Review queue", exact=True)).to_have_attribute("href", REVIEW_URL)
        expect(main.get_by_role("link", name="Trends", exact=True)).to_have_attribute("href", TRENDS_URL)
        expect(main.get_by_role("link", name="Submit application", exact=True)).to_have_attribute("href", CREATE_URL)

        expect(search_box(page)).to_be_visible()
        assert category_select(page).locator("option").all_inner_texts() == ["All categories"] + CATEGORIES
        assert sort_select(page).locator("option").all_inner_texts() == list(SORTS.values())
        expect(sort_select(page)).to_have_value("latest")
        expect(mine_switch(page)).to_have_attribute("aria-checked", "false")
        for label in ["All platforms"] + list(PLATFORMS.values()):
            expect(platform_chip(page, label)).to_be_visible()
        expect(result_count(page)).to_be_visible()

        browser.close()
