from playwright.sync_api import sync_playwright
from utils.app_releases_helper import (open_browser, open_releases, card_values, history_rows, current_row,
                                       PLATFORMS, APP_RELEASES_URL)


def test_card_matches_current_row():
    """AR-004: History has exactly one Current row per platform, and it shows the same release as the card.
    Each platform is checked in History filtered to it, since its Current row can be past page 1 unfiltered."""
    with sync_playwright() as p:
        browser, page = open_browser(p)

        for platform, label in PLATFORMS.items():
            open_releases(page, f"{APP_RELEASES_URL}?platform={platform}")
            rows = history_rows(page)
            assert [r for r in rows if "Current" in r["badges"]] == rows[:1], (label, [r["badges"] for r in rows])
            row = current_row(page, platform)
            c = card_values(page, platform)
            assert (row["platform"], row["latest"], row["min"]) == (label, c["latest"], c["min"]), (row, c)
            assert c["published"] == f"Published {row['published']} by {row['by']}", (row, c)

        browser.close()
