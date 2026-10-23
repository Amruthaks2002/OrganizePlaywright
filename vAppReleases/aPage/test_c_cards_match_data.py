from playwright.sync_api import sync_playwright
from utils.app_releases_helper import open_browser, open_releases, page_props, card_values, published_text, PLATFORMS


def test_cards_match_data():
    """AR-003: each platform card shows its current release's latest, minimum and 'Published <date> by <name>'."""
    with sync_playwright() as p:
        browser, page = open_browser(p)
        open_releases(page)
        current = page_props(page)["current"]

        for platform in PLATFORMS:
            release = current[platform]
            assert card_values(page, platform) == {
                "latest": release["latest_version"],
                "min": release["min_version"],
                "published": f"Published {published_text(release['created_at'])} by {release['created_by']}",
            }, platform

        browser.close()
