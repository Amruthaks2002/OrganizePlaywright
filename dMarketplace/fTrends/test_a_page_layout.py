from playwright.sync_api import sync_playwright, expect
from utils.marketplace_helper import (
    open_browser, open_marketplace, open_trends, main_content, trend_tile, trend_totals, TRENDS_URL,
)

TILES = {"Total downloads": "downloads", "Total kudos": "kudos", "Published apps": "published",
         "Pending review": "pending"}


def test_page_layout():
    """MP-043: Trends opens from the marketplace and shows the four stat tiles (matching the
    server's totals), the app of the day, the trending list with its period tabs and both
    monthly charts."""
    with sync_playwright() as p:
        browser, page = open_browser(p)

        open_marketplace(page)
        main_content(page).get_by_role("link", name="Trends", exact=True).click()
        page.wait_for_url(TRENDS_URL)
        open_trends(page)
        main = main_content(page)
        expect(main.get_by_text("How downloads and peer recognition are moving, month over month.")).to_be_visible()

        totals = trend_totals(page)
        for label, key in TILES.items():
            assert trend_tile(page, label) == int(totals[key]), f"{label}: {trend_tile(page, label)} vs {totals}"

        for heading in ["App of the day", "Trending apps", "Downloads", "Kudos"]:
            expect(main.get_by_role("heading", name=heading, exact=True)).to_be_visible()
        expect(main.get_by_text("Monthly downloads across all published apps")).to_be_visible()
        expect(main.get_by_text("Monthly peer endorsements given")).to_be_visible()
        for tab in ["Today", "This week", "This month"]:
            main.get_by_role("button", name=tab, exact=True).click()

        browser.close()
