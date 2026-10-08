from playwright.sync_api import sync_playwright, expect
from utils.dashboard_helper import open_browser_as, main_content, LEGEND


def test_legend():
    """DB-030: the colour key lists Leave, Work Mode, Holiday, Birthday, Anniversary and Note."""
    with sync_playwright() as p:
        browser, page = open_browser_as(p, "admin")
        legend = main_content(page).locator("div").filter(has_text="Anniversary").filter(
            has=page.get_by_text("Note", exact=True)).last
        for label in LEGEND:
            expect(legend.get_by_text(label, exact=True)).to_be_visible()
        browser.close()
