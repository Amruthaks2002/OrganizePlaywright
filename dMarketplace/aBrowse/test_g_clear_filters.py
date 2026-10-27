import re

from playwright.sync_api import sync_playwright, expect
from utils.marketplace_helper import (
    open_browser, open_marketplace, main_content, search_box, category_select, sort_select, mine_switch,
    result_count, clear_filters_button, MARKETPLACE_URL,
)


def test_clear_filters():
    """MP-007: 'Clear filters' resets search, category, platform, sort and My submissions."""
    with sync_playwright() as p:
        browser, page = open_browser(p)

        open_marketplace(page)
        expect(clear_filters_button(page)).to_have_count(0)

        open_marketplace(page, search="no-such-app-zzqx", category="Reporting", platform="idea", sort="kudos",
                         mine=True)
        expect(result_count(page)).to_have_text("0 results")
        expect(main_content(page).get_by_text("You haven't submitted anything yet.")).to_be_visible()
        expect(search_box(page)).to_have_value("no-such-app-zzqx")
        expect(category_select(page)).to_have_value("Reporting")
        expect(sort_select(page)).to_have_value("kudos")
        expect(mine_switch(page)).to_have_attribute("aria-checked", "true")
        expect(clear_filters_button(page)).to_have_text(re.compile(r"Clear filters\s*5$"))

        clear_filters_button(page).click()
        page.wait_for_url(MARKETPLACE_URL)
        expect(search_box(page)).to_have_value("")
        expect(category_select(page)).to_have_value("All categories")
        expect(sort_select(page)).to_have_value("latest")
        expect(mine_switch(page)).to_have_attribute("aria-checked", "false")
        # compare with a fresh unfiltered load rather than one taken at the start, so an app added or
        # removed elsewhere on QC mid-test does not fail it
        fresh = page.context.new_page()
        open_marketplace(fresh)
        expect(result_count(page)).to_have_text(result_count(fresh).inner_text())
        expect(result_count(page)).not_to_have_text("0 results")
        expect(clear_filters_button(page)).to_have_count(0)

        browser.close()
