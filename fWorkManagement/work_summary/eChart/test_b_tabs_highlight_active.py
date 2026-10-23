from playwright.sync_api import sync_playwright, expect
from utils.work_summary_helper import (open_browser, open_hours, open_tab, tab_button, is_active_tab, main_content, TABS)


def test_tabs_highlight_active():
    """WS-036: exactly one view tab is highlighted - Chart View on load, then whichever tab was clicked - and
    each tab shows its own content (chart, regular table, comp table)."""
    with sync_playwright() as p:
        browser, page = open_browser(p)
        open_hours(page)
        main = main_content(page)
        assert [t for t in TABS if is_active_tab(page, t)] == ["Chart View"]
        expect(main.locator("canvas")).to_be_visible()

        open_tab(page, "Regular Hours")
        assert [t for t in TABS if is_active_tab(page, t)] == ["Regular Hours"]
        expect(main.locator("canvas")).to_have_count(0)
        expect(main.locator("table thead")).not_to_contain_text("Comp Off Status")

        open_tab(page, "Comp Hours")
        assert [t for t in TABS if is_active_tab(page, t)] == ["Comp Hours"]
        expect(main.locator("table thead")).to_contain_text("Comp Off Status")

        tab_button(page, "Chart View").click()
        assert [t for t in TABS if is_active_tab(page, t)] == ["Chart View"]
        expect(main.locator("canvas")).to_be_visible()
        expect(main.locator("table")).to_have_count(0)

        browser.close()
